#version 430

layout(local_size_x = 1, local_size_y = 1) in;

struct Camera {
    vec3 position;
    vec3 forward;
    vec3 up;
    vec3 right;
};
struct Node {
    vec3 min_corner;
    vec3 max_corner;
    int index;
    int hit_link;
    int miss_link;
    int id_offset;
    int id_count;
};

struct Ray {
    vec3 origin;
    vec3 dir;
    float distance_traveled;
};
struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
};
struct AABB {
    ivec3 position;
    ivec3 size;
};
struct Node { //sizeof(Node) == 4*8 == 32 bytes
    uint children[8];
}


int MAX_DISTANCE = 500;
uniform Camera camera;
// uniform vec3 camera_position;
// uniform vec3 camera_forward;
// uniform vec3 camera_up;
// uniform vec3 camera_right;
layout(rgba32f, binding = 0) writeonly uniform image2D output_image;
layout(rgba32f, binding = 1) readonly  uniform image2D nodes;

float hitAABB(in Ray ray,in AABB box, inout t) {
    // Find the t values along each axis when the ray hits the box min values and max_values
    vec3 tMin = (box.position - ray.origin) / ray.dir;
    vec3 tMax = (box.position + box.size - ray.origin) / ray.dir; 
    // Sort the values to get the closer t values along each axis
    vec3 t1 = min(tMin,tMax);
    vec3 t2 = max(tMin,tMax);
    float tNear = max(t1.x,max(t1.y,t2.z));// the idea behind getting the maximum is that in order for the ray to be intersecting with the box, all axis must have heen hit.
    float tFar = min(t2.x,min(t2.y,t2.z));
    bool ret = tNear <= tFar && tFar > 0 && tNear < t;  // both tFar & tNear must be positive but since tFar is the upper bound of tNear then only tFar needs to be checked for positivity(?...)
    t = min(tNear,t);
    return ret;
}

Node getNodeByIndex(in int index) {
    Node node;
    for (int i = 0; i < 8; i+=2) {
        uvec4 val = imageLoad(nodes, ivec2(i,index));
        node.children[i] = (val.x << 8) | (val.y);
        node.children[i+1] = (val.z << 24) | (val.z << 16);
    }
   return node;
}

AABB splitAABB(in AABB box, in int index) {
    ivec3 overs = ivec3(
        (index >> 0) & 1,
        (index >> 1) & 1,
        (index >> 2) & 1
    );
    AABB new;
    new.size =  box.size / 2;;
    new.position = box.position + new.size * overs;
    return new;
}

vec3 CastRay(Ray ray) {
    vec3 out_color = vec3(0.0);
    float t;
    // Declare Stacks
    uint index = 0;
    Node stack[10];
    AABBB box_stack[10];
    
    // Initialize Stacks with starting values
    stack[0] = getNodeByIndex(0);
    box_stack[0].position = ivec3(0,0,0);
    box_stack[0].size = ivec3(512,512,512);
    bool hit = false;
    float t = 0;
    float ray_dist = 0.0;
    while (!hit && (ray_dist < MAX_DISTANCE)) {
        Node node = stack[pointer];
        AABB box = box_stack[pointer];
        bool intersect_aabb = hitAABB(ray,box,t);
        if (intersect_aabb) {
            // Calculate where it hit.
            vec3 hit_point = ray.origin + ray.dir * t;
            ray_dist += length(ray.dir * t);
            // if (box.size.x == 1) {
            //     // There are no more subdivisions to traverse, this nodes children will be indexes to 
            // } 
            // Calculate which box (of the 8 possible ones) it hit
            ivec3 half_size = box.size / 2;
            bool over_half_x = x >= ox + half_size.x;
            bool over_half_y = y >= oy + half_size.y;
            bool over_half_z = z >= oz + half_size.z;
            int i = int(over_half_x) + int(over_half_y) * 2 + int(over_half_z) * 4;
            int next_child_index = node.children[i];        
            if (next_child_index != 0) {
                pointer++;
                stack[pointer] = getNodeByIndex(next_child_index);
                box_stack[pointer] = splitAABB(box,i);
            } else {
                return 5.0 / (vec3(ray_dist) + 5.0);
            }
        } else {
            pointer--; // Pop the stack
        }

    }

}



 
// vec3 camera_right = cross(camera.forward,camera.up);

void main() {
    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
    ivec2 screen_size = imageSize(output_image);
    vec2 uv = vec2(pixel_coords) / screen_size;   

    float horizontalCoef = (float(pixel_coords.x)*2 - screen_size.x) / screen_size.x; 
    float verticalCoef   = (float(pixel_coords.y)*2 - screen_size.y) / screen_size.x; 

    Ray ray;
    ray.origin = camera.position;
    ray.dir = camera.forward + horizontalCoef * camera.right + verticalCoef * camera.up;
    ray.dir = normalize(ray.dir);
    ray.distance_traveled = 0.0;
    // while (ray.distance_traveled < MAX_DISTANCE) {
    //     ray
    // }

    Sphere sphere;
    sphere.center = vec3(1,0,0);
    sphere.radius = 0.5;
    sphere.color = vec3(0,1,0);

    // // Raytracing logic here
    float a = dot(ray.dir,ray.dir);
    float b = 2.0 * dot(ray.dir,ray.origin-sphere.center);
    float c = dot(ray.origin- sphere.center,ray.origin - sphere.center) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;
    vec3 color = vec3(0);
    // if (discriminant > 0) {
    //     color += sphere.color;
    // }
    float fog = 1.0 - (x / (x+10));

    color += sphere.color * step(0,discriminant) ;//*dot(ray.dir,ray.origin-sphere.center));


    imageStore(output_image, ivec2(gl_GlobalInvocationID.xy), vec4(color.bgr, 1.0));
}