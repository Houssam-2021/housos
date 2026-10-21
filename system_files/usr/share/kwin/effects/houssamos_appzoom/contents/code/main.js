/*
    HoussamOS App Zoom: windows grow out of their dock icon when they open and shrink back into
    it when they close or minimize, with a curve close to iOS (quick start, soft landing).
    Opening is a little slower than closing, as on iOS.

    Based on KWin's Scale and Squash effects.
    SPDX-License-Identifier: GPL-2.0-or-later
*/

"use strict";

// Windows that other effects animate or that must stay still (from KWin's Scale effect)
const blacklist = [
    "ksmserver ksmserver",
    "ksmserver-logout-greeter ksmserver-logout-greeter",
    "ksplashqml ksplashqml",
    "spectacle spectacle",
    "spectacle org.kde.spectacle",
];

// A window that has just opened has no dock icon position yet, so it grows from the middle of
// the dock instead. DOCK_HEIGHT matches branding/make_theme.py.
const DOCK_HEIGHT = 64;
const DOCK_GAP = 8;
const ICON_SIZE = 44;

// QEasingCurve.OutQuart is the closest of KWin's curves to iOS's cubic-bezier(0.32, 0.72, 0, 1)
const CURVE = QEasingCurve.OutQuart;

class AppZoomEffect {
    constructor() {
        effect.configChanged.connect(this.loadConfig.bind(this));
        effect.animationEnded.connect(this.cleanupForcedRoles.bind(this));
        effects.windowAdded.connect(this.slotWindowAdded.bind(this));
        effects.windowClosed.connect(this.slotWindowClosed.bind(this));
        effects.windowDataChanged.connect(this.slotWindowDataChanged.bind(this));
        for (const window of effects.stackingOrder) {
            this.watchMinimize(window);
        }
        this.loadConfig();
    }

    loadConfig() {
        this.openDuration = animationTime(effect.readConfig("OpenDuration", 520) || 520);
        this.closeDuration = animationTime(effect.readConfig("CloseDuration", 375) || 375);
    }

    static isAnimated(window) {
        // plasmashell's own windows (panels, popups) aren't animated, but its settings
        // dialogs are; they are the ones with a title bar
        if (window.windowClass == "plasmashell plasmashell"
                || window.windowClass == "plasmashell org.kde.plasmashell") {
            return window.hasDecoration;
        }
        if (blacklist.indexOf(window.windowClass) != -1) {
            return false;
        }
        // Games and other full screen windows appear at once
        if (window.fullScreen) {
            return false;
        }
        if (window.hasDecoration) {
            return true;
        }
        if (window.popupWindow || window.lockScreen || window.outline || !window.managed) {
            return false;
        }
        return window.normalWindow || window.dialog;
    }

    static hasIcon(window) {
        const icon = window.iconGeometry;
        return !!icon && icon.width > 0 && icon.height > 0;
    }

    static screenGeometry(window) {
        try {
            const geometry = window.screen.geometry;
            if (geometry && geometry.width > 0) {
                return geometry;
            }
        } catch (error) {
            // fall through to the whole desktop
        }
        return effects.virtualScreenGeometry;
    }

    // The window's dock icon, or the middle of the dock when KWin doesn't know it yet
    static iconRect(window) {
        if (AppZoomEffect.hasIcon(window)) {
            return window.iconGeometry;
        }
        const screen = AppZoomEffect.screenGeometry(window);
        return {
            x: screen.x + (screen.width - ICON_SIZE) / 2,
            y: screen.y + screen.height - DOCK_GAP - (DOCK_HEIGHT + ICON_SIZE) / 2,
            width: ICON_SIZE,
            height: ICON_SIZE,
        };
    }

    // Size and position animations between the window and an icon (as in KWin's Squash effect)
    static zoom(window, icon, intoIcon) {
        const frame = window.geometry;
        const frameSize = { value1: frame.width, value2: frame.height };
        const iconSize = { value1: icon.width, value2: icon.height };
        const atFrame = { value1: 0.0, value2: 0.0 };
        const atIcon = {
            value1: icon.x - frame.x - (frame.width - icon.width) / 2,
            value2: icon.y - frame.y - (frame.height - icon.height) / 2,
        };
        return [
            {
                type: Effect.Size,
                from: intoIcon ? frameSize : iconSize,
                to: intoIcon ? iconSize : frameSize,
            },
            {
                type: Effect.Translation,
                from: intoIcon ? atFrame : atIcon,
                to: intoIcon ? atIcon : atFrame,
            },
        ];
    }

    // Grow out of the icon; the window becomes opaque in the first part of the movement
    zoomOut(window, icon) {
        return animate({
            window: window,
            curve: CURVE,
            duration: this.openDuration,
            animations: AppZoomEffect.zoom(window, icon, false).concat([{
                type: Effect.Opacity,
                from: 0.0,
                to: 1.0,
                curve: QEasingCurve.OutCubic,
                duration: Math.round(this.openDuration * 0.4),
            }]),
        });
    }

    // Shrink into the icon; the window fades out only near the end
    zoomIn(window, icon) {
        return animate({
            window: window,
            curve: CURVE,
            duration: this.closeDuration,
            animations: AppZoomEffect.zoom(window, icon, true).concat([{
                type: Effect.Opacity,
                from: 1.0,
                to: 0.0,
                curve: QEasingCurve.InQuad,
            }]),
        });
    }

    setupForcedRoles(window) {
        window.setData(Effect.WindowForceBackgroundContrastRole, true);
        window.setData(Effect.WindowForceBlurRole, true);
    }

    cleanupForcedRoles(window) {
        window.setData(Effect.WindowForceBackgroundContrastRole, null);
        window.setData(Effect.WindowForceBlurRole, null);
    }

    slotWindowAdded(window) {
        this.watchMinimize(window);
        if (effects.hasActiveFullScreenEffect) {
            return;
        }
        if (!AppZoomEffect.isAnimated(window) || !window.visible) {
            return;
        }
        if (effect.isGrabbed(window, Effect.WindowAddedGrabRole)) {
            return;
        }
        this.setupForcedRoles(window);
        if (window.normalWindow) {
            window.appZoomOpen = this.zoomOut(window, AppZoomEffect.iconRect(window));
        } else {
            // Dialogs open in place
            window.appZoomOpen = animate({
                window: window,
                curve: QEasingCurve.OutCubic,
                duration: Math.round(this.openDuration * 0.45),
                animations: [
                    { type: Effect.Scale, from: 0.9 },
                    { type: Effect.Opacity, from: 0.0 },
                ],
            });
        }
    }

    slotWindowClosed(window) {
        if (effects.hasActiveFullScreenEffect) {
            return;
        }
        if (!AppZoomEffect.isAnimated(window)) {
            return;
        }
        if (!window.visible || window.skipsCloseAnimation) {
            return;
        }
        if (effect.isGrabbed(window, Effect.WindowClosedGrabRole)) {
            return;
        }
        if (window.appZoomOpen) {
            cancel(window.appZoomOpen);
            delete window.appZoomOpen;
        }
        this.setupForcedRoles(window);
        if (window.normalWindow && AppZoomEffect.hasIcon(window)) {
            window.appZoomClose = this.zoomIn(window, window.iconGeometry);
        } else {
            window.appZoomClose = animate({
                window: window,
                curve: QEasingCurve.InCubic,
                duration: Math.round(this.closeDuration * 0.55),
                animations: [
                    { type: Effect.Scale, to: 0.9 },
                    { type: Effect.Opacity, to: 0.0 },
                ],
            });
        }
    }

    slotWindowDataChanged(window, role) {
        if (role == Effect.WindowAddedGrabRole) {
            if (window.appZoomOpen && effect.isGrabbed(window, role)) {
                cancel(window.appZoomOpen);
                delete window.appZoomOpen;
                this.cleanupForcedRoles(window);
            }
        } else if (role == Effect.WindowClosedGrabRole) {
            if (window.appZoomClose && effect.isGrabbed(window, role)) {
                cancel(window.appZoomClose);
                delete window.appZoomClose;
                this.cleanupForcedRoles(window);
            }
        }
    }

    watchMinimize(window) {
        window.minimizedChanged.connect(() => {
            if (window.minimized) {
                this.slotWindowMinimized(window);
            } else {
                this.slotWindowUnminimized(window);
            }
        });
    }

    slotWindowMinimized(window) {
        if (effects.hasActiveFullScreenEffect || !AppZoomEffect.hasIcon(window)) {
            return;
        }
        if (window.appZoomRestore) {
            if (redirect(window.appZoomRestore, Effect.Backward)) {
                return;
            }
            cancel(window.appZoomRestore);
            delete window.appZoomRestore;
        }
        if (window.appZoomMinimize) {
            if (redirect(window.appZoomMinimize, Effect.Forward)) {
                return;
            }
            cancel(window.appZoomMinimize);
        }
        window.setData(Effect.WindowForceBlurRole, true);
        window.appZoomMinimize = this.zoomIn(window, window.iconGeometry);
    }

    slotWindowUnminimized(window) {
        if (effects.hasActiveFullScreenEffect || !AppZoomEffect.hasIcon(window)) {
            return;
        }
        if (window.appZoomMinimize) {
            if (redirect(window.appZoomMinimize, Effect.Backward)) {
                return;
            }
            cancel(window.appZoomMinimize);
            delete window.appZoomMinimize;
        }
        if (window.appZoomRestore) {
            if (redirect(window.appZoomRestore, Effect.Forward)) {
                return;
            }
            cancel(window.appZoomRestore);
        }
        window.setData(Effect.WindowForceBlurRole, true);
        window.appZoomRestore = this.zoomOut(window, window.iconGeometry);
    }
}

new AppZoomEffect();
