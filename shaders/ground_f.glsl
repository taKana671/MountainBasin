#version 300 es
precision highp float;

uniform float tex_ScaleFactor0;
uniform float tex_ScaleFactor1;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D tex_attribute;

in vec2 texcoord0;
in vec2 texcoord1;
in vec2 texcoord_g;
in vec4 vertex;

out vec4 fragColor;


void main() {
    // tex_moss
    vec3 tex0 = texture(p3d_Texture0, texcoord0.st * tex_ScaleFactor0).rgb;

    // tex_ground_rock
    vec3 tex1 = texture(p3d_Texture1, texcoord1.st * tex_ScaleFactor1).rgb;

    // ground mask image
    vec3 tex_g = texture(p3d_Texture2, texcoord_g.st).rgb;

    float w = tex_g.r;
    vec3 color = tex1.rgb * w + tex0 * (1.0 - w);
    fragColor = vec4(color, 1.0);
}