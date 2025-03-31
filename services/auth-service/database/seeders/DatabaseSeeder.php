<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // \App\Models\User::factory(10)->create();

        // \App\Models\User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);

        // Skip RolesAndPermissionsSeeder if permissions already exist
        try {
            $this->call(RolesAndPermissionsSeeder::class);
        } catch (\Exception $e) {
            $this->command->info('Roles and permissions already exist. Skipping seeder.');
        }
        
        $this->call(AdminUserSeeder::class);
    }
}
