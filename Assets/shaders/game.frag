#version 330 core

uniform sampler2D world_tex;
uniform sampler2D ui_tex;
uniform float light;
uniform float danger;
in vec2 uvs;
out vec4 f_color;

float hypot(float x, float y) {
    return sqrt(x*x+y*y);
}
float distance_to_edge( vec2 coord) {
    return hypot(abs(coord.x-.5)*1.414,abs(coord.y-.5)*1.414);
}
vec4 addOnTop(vec4 canvas, vec4 source) {
    return vec4(canvas.rgb * (1-source.a) + source.rgb * source.a , max(canvas.a,source.a));
}

void main() {
    // vec4 red_overlay = vec4(.5,0.0,0.0,distance_to_edge(uvs) * danger); 
    // vec4 color = vec4(texture(world_tex,uvs).rgb,1.0);
    // color = vec4(addOnTop(color,red_overlay).rgb * light,1.0);
    // f_color = addOnTop(color,texture(ui_tex,uvs));
    
    f_color = addOnTop(texture(world_tex,uvs),texture(ui_tex,uvs));
    f_color.a = 1.0;
}