<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class FixedUsersSeeder extends Seeder
{
    public function run(): void
    {
        $employees = [
            ['id' => 1001, 'name' => 'بنور'],
            ['id' => 1002, 'name' => 'عماد'],
            ['id' => 1003, 'name' => 'علي'],
            ['id' => 1004, 'name' => 'طه'],
        ];

        foreach ($employees as $employee) {
            DB::table('users')->updateOrInsert(
                ['id' => $employee['id']],
                [
                    'name' => $employee['name'],
                    'email' => $employee['id'] . '@example.com',
                    'password' => Hash::make('12345'),
                    'role' => 'employee',
                ]
            );
        }

        $managers = [
            ['id' => 1, 'name' => 'عادل'],
            ['id' => 2, 'name' => 'عبدالرؤوف'],
            ['id' => 3, 'name' => 'سالم'],
        ];

        foreach ($managers as $manager) {
            DB::table('users')->updateOrInsert(
                ['id' => $manager['id']],
                [
                    'name' => $manager['name'],
                    'email' => $manager['id'] . '@example.com',
                    'password' => Hash::make('507799'),
                    'role' => 'manager',
                ]
            );
        }
    }
}
