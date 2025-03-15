#version 430 core
#define CHUNK_SIZE 64
#define BOUNCES 1 
struct Camera {
    vec3 position;
    vec3 forward;
    vec3 up;
    vec3 right;
};
struct Ray {
    vec3 origin;
    vec3 direction;
};

struct HitRecord {
    vec3 p;
    float t;
    vec3 normal;
    vec3 color;  // should be replaced by material
};
struct AABB {
    ivec3 position;
    ivec3 size;
};
struct Node {
    uint children[8];
    AABB box;
};


layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) writeonly uniform image2D output_image;
layout(rgba8ui, binding = 1) readonly uniform uimage3D data; // 3D Voxel Data
layout(rgba16ui, binding =2) readonly uniform uimage1D octree; // Octree : 16*4 = 64 bits = 8 bytes
// <data> image is rgba8ui meaning that each channel (of the uvec4 it returns) is 8 bits so the vec4 in total is (8 bits)*(4 channels) == 32 bits == 4 bytes
uniform Camera camera;




bool voxelPresent(ivec3 voxel_position, out vec3 color) {
    uvec4 voxel = imageLoad(data,voxel_position);
    // color.r = float(voxel.r) / 255.0; // uint -> float
    // color.g = float(voxel.g) / 255.0; // uint -> float
    // color.b = float(voxel.b) / 255.0; // uint -> float
    color = vec3(voxel.rgb) / 255.0;
    return voxel.a != 0;
    // return voxel.a == 0;
}
uint[8] loadOctreeChildrenByIndex(uint index) {
    uvec4 voxel = imageLoad(octree,index);
    Node n;
    n.children[0] = voxel.r >> 8;
    n.children[1] = voxel.r & 255;
    n.children[2] = voxel.g >> 8;
    n.children[3] = voxel.g & 255;
    n.children[4] = voxel.b >> 8;
    n.children[5] = voxel.b & 255;
    n.children[6] = voxel.a >> 8;
    n.children[7] = voxel.a & 255;
    return n;
}
bool hitAABB(in Ray ray,in AABB box, inout t) {
    // Find the t values along each axis when the ray hits the box min values and max_values
    vec3 tMin = (box.position - ray.origin) / ray.direction;
    vec3 tMax = (box.position + box.size - ray.origin) / ray.direction; 
    // Sort the values to get the closer t values along each axis
    vec3 t1 = min(tMin,tMax);
    vec3 t2 = max(tMin,tMax);
    float tNear = max(t1.x,max(t1.y,t2.z));// the idea behind getting the maximum is that in order for the ray to be intersecting with the box, all axis must have heen hit.
    float tFar = min(t2.x,min(t2.y,t2.z));
    bool ret = tNear <= tFar && tFar > 0 && tNear < t;  // both tFar & tNear must be positive but since tFar is the upper bound of tNear then only tFar needs to be checked for positivity(?...)
    t = min(tNear,t);
    return ret;
}
AABB splitAABB(in AABB box, in bvec3 overs) {
    return  AABB(
        box.position + new.size * vec3(overs),
        box.size / 2 ;
    );
    // AABB new;
    // new.size =  box.size / 2;;
    // new.position = box.position + new.size * vec3(overs);
    // return new;
}

interface AABB {
    Vector3 Center; // Center point of the bounding box
    Plane[] MidPlanes = new[] { // These are the planes which split a bounding box in half in each direction
            new Plane(Vector3.UnitZ, Center.Z),
            new Plane(Vector3.UnitY, Center.Y),
            new Plane(Vector3.UnitX, Center.X)
        };
    bool Contains(Vector3 point); // True if the point lies within the bounding box
}

class Octree {
    bool Empty; // Whether this octant contains nothing
    Octree[] Nodes; // This is an array of 8 child octants, laid out where 0 bits correspond to the negative side of the plane, 1 bits are positive
                    // X == 4, Y == 2, Z == 1
    AABB BoundingBox; // Axis-aligned bounding box for this octant
    Mesh Leaf; // Triangles for a given leaf octant
    vec3 RayIntersection(Octree tree, vec3 rayOrigin, vec3 rayDir) {
        vec3 position;
        OctreeNode node = tree;
        if (isLeaf(node)){
            return getColorOfChunk(rayOrigin,rayDir);
        }
        bvec3 side = bvec3(dot(rayOrigin,vec3(1,0,0)) - tree.center.x >= 0, 
                           dot(rayOrigin,vec3(0,1,0)) - tree.center.y >= 0,
                           dot(rayOrigin,vec3(0,0,1)) - tree.center.z >= 0);
        float xDist,yDist,zDist;
        if (side.x == rayDir.x < 0) {
            xDist = PlaneRayDistance(vec3(1,0,0),tree.center.x,rayOrigin,rayDir);
        } else {
            xDist = 1.0 / 0.0;
        }
        if (side.y == rayDir.y < 0) {
            yDist = PlaneRayDistance(vec3(0,1,0),tree.center.y,rayOrigin,rayDir);
        } else {
            yDist = 1.0 / 0.0;
        }
        if (side.z == rayDir.z < 0) {
            zDist = PlaneRayDistance(vec3(0,0,1),tree.center.z,rayOrigin,rayDir);
        } else {
            zDist = 1.0 / 0.0;
        }
    }
    (Triangle, Vector3)? RayIntersection(Vector3 _origin, Vector3 direction) {
        if(Empty) return null;
        var origin = _origin;
        if(Leaf != null) return Leaf.RayIntersection(origin, direction);

        var planes = BoundingBox.MidPlanes;
        var side = (
            X: Vector3.Dot(origin, planes[2].Normal) - planes[2].Distance >= 0,
            Y: Vector3.Dot(origin, planes[1].Normal) - planes[1].Distance >= 0,
            Z: Vector3.Dot(origin, planes[0].Normal) - planes[0].Distance >= 0
        );
        var xDist = side.X == direction.X < 0
            ? planes[2].RayDistance(origin, direction)
            : float.PositiveInfinity;
        var yDist = side.Y == direction.Y < 0
            ? planes[1].RayDistance(origin, direction)
            : float.PositiveInfinity;
        var zDist = side.Z == direction.Z < 0
            ? planes[0].RayDistance(origin, direction)
            : float.PositiveInfinity;
        for(var i = 0; i < 3; ++i) {
            var idx = (side.Z ? 1 : 0) | (side.Y ? 2 : 0) | (side.X ? 4 : 0);
            var ret = Nodes[idx].RayIntersection(origin, direction);
            if(ret != null) return ret;

            var minDist = MathF.Min(MathF.Min(xDist, yDist), zDist);
            if(float.IsInfinity(minDist)) return null;

            origin = _origin + direction * minDist;
            if(!BoundingBox.Contains(origin)) return null;
            if(minDist == xDist) { side.X = !side.X; xDist = float.PositiveInfinity; }
            else if(minDist == yDist) { side.Y = !side.Y; yDist = float.PositiveInfinity; }
            else if(minDist == zDist) { side.Z = !side.Z; zDist = float.PositiveInfinity; }
        }

        return null;
    }
}


bool voxelMarchOctree(Ray ray, out HitRecord rec) {
    // Start with the root node
    Node cur;
    cur.children = loadOctreeChildrenByIndex(0);
    cur.box.position = ivec3(0);
    cur.box.size = ivec3(64)
    uint layer_in = 0;
    for (int i=0;i<64;i++) {
        float t;
        if (hitAABB(ray,root.box,t)) {
            vec3 ray_intersection = ray.origin + ray.direction * t;
            ivec3 half_size = box.size / 2;
            bvec3 overs = greaterThanEqual(ivec3(ray_intersection),cur.box.position + box.size / 2);
            int child_index = int(overs.x) + int(overs.y) * 2 + int(overs.z) * 4;
            uint image_index = cur.children[child_index];
            if (image_index != 0) {
                cur.children = loadOctreeChildrenByIndex(image_index);
                cur.box = splitAABB(cur.box,bvec3(over_half_x,over_half_y,over_half_z))
                layer_int++;
            } else {
                // This child is empty. It does not contain any blocks
                //move Ray to the position it is in plus a tiny bit and continue
                ray.origin = ray_intersection + ray.direction * 0.001;
                ray                 
            }

        }
    }

}

// DDA Ray Voxel March (with incorrect distance return)
bool voxelMarch(Ray ray, out HitRecord rec) {
	ivec3 mapPos = ivec3(floor(ray.origin + 0.)); // Current Voxel 
    vec3 deltaDist = abs(vec3(length(ray.direction)) / ray.direction); // abs(1/ray.direction)? 
	ivec3 rayStep = ivec3(sign(ray.direction));
	vec3 sideDist = (sign(ray.direction) * (vec3(mapPos) - ray.origin) + (sign(ray.direction) * 0.5) + 0.5) * deltaDist; 
    bvec3 mask;
    for (int i = 0; i < 100;i++){
        bool present = voxelPresent(mapPos, rec.color);        
        if (present) {
            vec3 tCube = (mapPos - ray.origin - 0.5*sign(ray.direction))/ray.direction;
            rec.t = max(tCube.x,max(tCube.y,tCube.z));
            rec.normal = vec3(mask);
            rec.p = ray.origin + ray.direction * rec.t;
            return true;
        }
        mask = lessThanEqual(sideDist.xyz, min(sideDist.yzx, sideDist.zxy));        
        sideDist += vec3(mask) * deltaDist;
        mapPos += ivec3(vec3(mask)) * rayStep;
    }
    return false;
}

bool worldHit(Ray ray, out HitRecord rec) {
    return voxelMarch(ray, rec);
}

float getShading(float d) {
    const float F = 64;
    return 1 - d/F;
}

Ray get_ray() {
    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
    ivec2 screen_size = imageSize(output_image);

    float horizontalCoef = (float(pixel_coords.x)*2 - screen_size.x) / screen_size.x; 
    float verticalCoef   = (float(pixel_coords.y)*2 - screen_size.y) / screen_size.x; 
    float focal_length = 1.0;

    return Ray(
        camera.position,
        normalize(
            focal_length * camera.forward + horizontalCoef * camera.right + verticalCoef * -camera.up
        )
    );
    // float aspect_ratio = image_size.x / image_size.y;

    // vec3 center = vec3(models[0].size.x / 2, models[0].size.y / 2, models[0].size.z + 12);

    // float focal_length = 1.0;
    // float viewport_height = 2.0;
    // float viewport_width = viewport_height * aspect_ratio;

    // vec3 viewport_u = vec3(viewport_width, 0.0, 0.0);
    // vec3 viewport_v = vec3(0.0, viewport_height, 0.0);

    // vec3 pixel_delta_u = viewport_u / image_width;
    // vec3 pixel_delta_v = viewport_v / image_height;

    // vec3 viewport_lower_left = center - vec3(0, 0, focal_length) - viewport_u / 2 - viewport_v / 2;

    // vec3 pixel00_loc = viewport_lower_left + 0.5 * (pixel_delta_u + pixel_delta_v);

    // return Ray(
    //     center,
    //     normalize((pixel00_loc + (gl_GlobalInvocationID.x) * pixel_delta_u
    //                            + (gl_GlobalInvocationID.y) * pixel_delta_v) - center)
    // );
}

vec3 get_color() {
    vec3 out_color = vec3(0, 0, 0);

    Ray ray = get_ray();

    HitRecord rec;
    bool hit = worldHit(ray,rec);
    if (hit) {
        return rec.color*getShading(rec.t);
    } else {
        return vec3(1);
    }
    
    
    // if (worldHit(ray, rec)) {
    //     // vec3 scatter_dir = rec.normal;//random Vector;
    //     // handle scatter_dir near zero case
    //     // if (scatter_dir.x < 1e-8 && scatter_dir.y < 1e-8 && scatter_dir.z < 1e-8) {
    //     //     scatter_dir = rec.normal;
    //     // }
    //     // ray.origin = rec.p + scatter_dir * 0.001;
    //     // ray.direction = normalize(scatter_dir);
    //     return rec.color;
    // } else {
    //     float a = 0.5 * (ray.direction.y + 1.0);
    //     return mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), a);
        
    // }
    // return out_color;
}





// void main() {
//     ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
//     ivec2 screen_size = imageSize(output_image);
   

//     imageStore(output_image, ivec2(gl_GlobalInvocationID.xy), vec4(color.bgr, 1.0));
// }


void main() {
    // vec4 color = vec4(imageLoad(data,0)) ;
    vec3 color = get_color();

    imageStore(output_image, ivec2(gl_GlobalInvocationID.xy), vec4(color.bgr,1.0));

}