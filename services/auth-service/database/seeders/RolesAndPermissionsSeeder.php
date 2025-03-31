<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

class RolesAndPermissionsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Reset cached roles and permissions
        app()[\Spatie\Permission\PermissionRegistrar::class]->forgetCachedPermissions();

        // Create permissions
        $permissions = [
            // User permissions
            'view users',
            'create users',
            'update users',
            'delete users',
            
            // Role permissions
            'view roles',
            'create roles',
            'update roles',
            'delete roles',
            'assign roles',
            
            // Permission-related permissions
            'view permissions',
            'assign permissions',
            
            // Agent permissions
            'view agents',
            'create agents',
            'update agents',
            'delete agents',
            'run agents',
            
            // System permissions
            'access settings',
            'view logs',
            'view metrics',
        ];

        foreach ($permissions as $permission) {
            Permission::create(['name' => $permission]);
        }

        // Create roles and assign permissions
        $adminRole = Role::create(['name' => 'admin']);
        $adminRole->givePermissionTo(Permission::all());

        $userRole = Role::create(['name' => 'user']);
        $userRole->givePermissionTo([
            'view agents',
            'create agents',
            'update agents',
            'delete agents',
            'run agents',
        ]);

        // Create default admin user
        $admin = User::create([
            'name' => 'Admin',
            'username' => 'admin',
            'email' => 'admin@example.com',
            'password' => Hash::make('admin123'),
            'email_verified_at' => now(),
        ]);
        $admin->assignRole($adminRole);

        // Create default regular user
        $user = User::create([
            'name' => 'Regular User',
            'username' => 'user',
            'email' => 'user@example.com',
            'password' => Hash::make('user123'),
            'email_verified_at' => now(),
        ]);
        $user->assignRole($userRole);
    }
} 