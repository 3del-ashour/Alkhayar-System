<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class FixedUsersSeeder extends Seeder
{
    public function run(): void
    {
        // ensure existing users have a safe employee_id to avoid collisions
        User::whereNull('employee_id')->orWhere('employee_id', '')->update(['employee_id' => '9999']);

        $users = [
            // Managers
            ['employee_id' => '1',    'name' => 'عادل',       'username' => 'adel',       'role' => 'manager',  'password' => '507799'],
            ['employee_id' => '2',    'name' => 'عبدالرؤوف', 'username' => 'abdelraouf', 'role' => 'manager',  'password' => '507799'],
            ['employee_id' => '3',    'name' => 'سالم',       'username' => 'salem',      'role' => 'manager',  'password' => '507799'],
            // Employees
            ['employee_id' => '1001', 'name' => 'بنور',       'username' => 'benoor',     'role' => 'employee', 'password' => '12345'],
            ['employee_id' => '1002', 'name' => 'عماد',       'username' => 'emad',       'role' => 'employee', 'password' => '12345'],
            ['employee_id' => '1003', 'name' => 'علي',        'username' => 'ali',        'role' => 'employee', 'password' => '12345'],
            ['employee_id' => '1004', 'name' => 'طه',         'username' => 'taha',       'role' => 'employee', 'password' => '12345'],
        ];

        foreach ($users as $u) {
            $user = User::updateOrCreate(
                ['employee_id' => $u['employee_id']],
                [
                    'name' => $u['name'],
                    'username' => $u['username'],
                    'role' => $u['role'],
                    'password' => Hash::make($u['password']),
                ]
            );

            $user->email = null;
            $user->save();
        }
    }
}
