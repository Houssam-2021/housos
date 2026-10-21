#version 140

// HoussamOS App Zoom: blurs the windows behind an app while it zooms, as iOS blurs the home
// screen. blurRadius (in pixels) is animated by contents/code/main.js; modulation carries the
// window's opacity and brightness, which the effect also animates.
// KWin turns "#version 140" into "#version 300 es" on OpenGL ES. Older OpenGL has no
// blur.frag, so there the shader doesn't load and apps zoom without the blur.

uniform sampler2D sampler;
uniform vec4 modulation;
uniform float blurRadius;

in vec2 texcoord0;
out vec4 fragColor;

void main(void)
{
    vec2 texel = blurRadius / vec2(textureSize(sampler, 0));
    vec4 sum = texture(sampler, texcoord0);
    float total = 1.0;
    // Three rings of eight samples, each ring turned a little, weighted like a gaussian
    for (int ring = 1; ring <= 3; ring++) {
        float radius = float(ring) / 3.0;
        float weight = exp(-radius * radius * 2.0);
        for (int i = 0; i < 8; i++) {
            float angle = radians(45.0 * float(i) + 15.0 * float(ring));
            sum += texture(sampler, texcoord0 + vec2(cos(angle), sin(angle)) * texel * radius) * weight;
            total += weight;
        }
    }
    fragColor = (sum / total) * modulation;
}
