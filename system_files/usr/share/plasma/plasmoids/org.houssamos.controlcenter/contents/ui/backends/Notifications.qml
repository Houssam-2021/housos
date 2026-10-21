import QtQuick
import org.kde.notificationmanager as NotificationManager

// Do Not Disturb, the way KDE's notifications widget sets it: until a year from now, and
// ending it clears the date and any app that asked for quiet
Item {
    readonly property bool doNotDisturb: {
        const until = settings.notificationsInhibitedUntil.getTime();
        return !isNaN(until) && until > Date.now();
    }

    function setDoNotDisturb(on) {
        if (on) {
            const until = new Date();
            until.setFullYear(until.getFullYear() + 1);
            settings.notificationsInhibitedUntil = until;
        } else {
            settings.notificationsInhibitedUntil = undefined;
            settings.revokeApplicationInhibitions();
        }
        settings.save();
    }

    NotificationManager.Settings {
        id: settings
    }
}
