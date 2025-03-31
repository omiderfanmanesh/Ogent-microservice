<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;

class RoleController extends Controller
{
    /**
     * Display a listing of roles.
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        $roles = Role::all();
        
        // Include permissions for each role
        $roles = $roles->map(function ($role) {
            $role->permissions = $role->permissions->pluck('name');
            return $role;
        });
        
        return response()->json($roles);
    }

    /**
     * Display the specified role.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function show($id)
    {
        $role = Role::findById($id);
        
        if (!$role) {
            return response()->json([
                'message' => 'Role not found'
            ], 404);
        }
        
        $role->permissions = $role->permissions->pluck('name');
        
        return response()->json($role);
    }

    /**
     * Store a newly created role.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255|unique:roles,name',
            'permissions' => 'sometimes|array',
            'permissions.*' => 'exists:permissions,name',
        ]);

        $role = Role::create(['name' => $request->name]);
        
        if ($request->has('permissions')) {
            $role->givePermissionTo($request->permissions);
        }
        
        $role->permissions = $role->permissions->pluck('name');
        
        return response()->json($role, 201);
    }

    /**
     * Update the specified role.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function update(Request $request, $id)
    {
        $role = Role::findById($id);
        
        if (!$role) {
            return response()->json([
                'message' => 'Role not found'
            ], 404);
        }
        
        $request->validate([
            'name' => 'sometimes|string|max:255|unique:roles,name,'.$role->id,
            'permissions' => 'sometimes|array',
            'permissions.*' => 'exists:permissions,name',
        ]);

        if ($request->has('name')) {
            $role->name = $request->name;
            $role->save();
        }
        
        if ($request->has('permissions')) {
            $role->syncPermissions($request->permissions);
        }
        
        $role->permissions = $role->permissions->pluck('name');
        
        return response()->json($role);
    }

    /**
     * Remove the specified role.
     *
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function destroy($id)
    {
        $role = Role::findById($id);
        
        if (!$role) {
            return response()->json([
                'message' => 'Role not found'
            ], 404);
        }
        
        // Prevent deleting essential roles
        if (in_array($role->name, ['admin', 'user'])) {
            return response()->json([
                'message' => 'Cannot delete essential roles'
            ], 403);
        }
        
        $role->delete();
        
        return response()->json([
            'message' => 'Role deleted successfully'
        ]);
    }

    /**
     * Get a list of all permissions.
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function permissions()
    {
        $permissions = Permission::all()->pluck('name');
        
        return response()->json($permissions);
    }

    /**
     * Assign permissions to a role.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function assignPermissions(Request $request, $id)
    {
        $role = Role::findById($id);
        
        if (!$role) {
            return response()->json([
                'message' => 'Role not found'
            ], 404);
        }
        
        $request->validate([
            'permissions' => 'required|array',
            'permissions.*' => 'exists:permissions,name',
        ]);
        
        $role->syncPermissions($request->permissions);
        
        return response()->json([
            'message' => 'Permissions assigned successfully',
            'permissions' => $role->permissions->pluck('name'),
        ]);
    }
} 