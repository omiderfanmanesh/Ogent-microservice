<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;

class RolePermissionTest extends TestCase
{
    use RefreshDatabase, WithFaker;

    /**
     * Setup the test environment.
     */
    protected function setUp(): void
    {
        parent::setUp();
        
        // Create permissions
        Permission::create(['name' => 'test permission']);
        Permission::create(['name' => 'another test permission']);
        
        // Create roles
        Role::create(['name' => 'test-role']);
        Role::create(['name' => 'admin-test']);
    }

    /**
     * Test creating a new role
     */
    public function test_role_can_be_created()
    {
        $roleName = 'new-role-' . $this->faker->word();
        
        $role = Role::create(['name' => $roleName]);
        
        $this->assertInstanceOf(Role::class, $role);
        $this->assertEquals($roleName, $role->name);
        
        $this->assertDatabaseHas('roles', [
            'name' => $roleName,
        ]);
    }
    
    /**
     * Test creating a new permission
     */
    public function test_permission_can_be_created()
    {
        $permissionName = 'new-permission-' . $this->faker->word();
        
        $permission = Permission::create(['name' => $permissionName]);
        
        $this->assertInstanceOf(Permission::class, $permission);
        $this->assertEquals($permissionName, $permission->name);
        
        $this->assertDatabaseHas('permissions', [
            'name' => $permissionName,
        ]);
    }
    
    /**
     * Test assigning a permission to a role
     */
    public function test_permission_can_be_assigned_to_role()
    {
        $role = Role::findByName('test-role');
        $permission = Permission::findByName('test permission');
        
        $role->givePermissionTo($permission);
        
        $this->assertTrue($role->hasPermissionTo($permission));
        
        $this->assertDatabaseHas('role_has_permissions', [
            'role_id' => $role->id,
            'permission_id' => $permission->id,
        ]);
    }
    
    /**
     * Test assigning a role to a user
     */
    public function test_role_can_be_assigned_to_user()
    {
        $user = User::factory()->create();
        $role = Role::findByName('test-role');
        
        $user->assignRole($role);
        
        $this->assertTrue($user->hasRole('test-role'));
        
        $this->assertDatabaseHas('model_has_roles', [
            'role_id' => $role->id,
            'model_id' => $user->id,
            'model_type' => User::class,
        ]);
    }
    
    /**
     * Test user has permission through role
     */
    public function test_user_has_permission_through_role()
    {
        $user = User::factory()->create();
        $role = Role::findByName('test-role');
        $permission = Permission::findByName('test permission');
        
        $role->givePermissionTo($permission);
        $user->assignRole($role);
        
        $this->assertTrue($user->hasPermissionTo('test permission'));
    }
    
    /**
     * Test revoking permissions from role
     */
    public function test_revoke_permission_from_role()
    {
        $role = Role::findByName('test-role');
        $permission = Permission::findByName('test permission');
        
        $role->givePermissionTo($permission);
        $this->assertTrue($role->hasPermissionTo($permission));
        
        $role->revokePermissionTo($permission);
        $this->assertFalse($role->hasPermissionTo($permission));
        
        $this->assertDatabaseMissing('role_has_permissions', [
            'role_id' => $role->id,
            'permission_id' => $permission->id,
        ]);
    }
    
    /**
     * Test removing role from user
     */
    public function test_remove_role_from_user()
    {
        $user = User::factory()->create();
        $role = Role::findByName('test-role');
        
        $user->assignRole($role);
        $this->assertTrue($user->hasRole('test-role'));
        
        $user->removeRole($role);
        $this->assertFalse($user->hasRole('test-role'));
        
        $this->assertDatabaseMissing('model_has_roles', [
            'role_id' => $role->id,
            'model_id' => $user->id,
            'model_type' => User::class,
        ]);
    }
} 