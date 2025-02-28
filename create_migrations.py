import os
from datetime import datetime

# Base timestamp for migrations
base_timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')

# Migration definitions
migrations = [
    {
        'name': 'create_roles_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('roles', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('roles');
    }
};'''
    },
    {
        'name': 'create_schools_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('schools', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('code')->unique();
            $table->text('description')->nullable();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('schools');
    }
};'''
    },
    {
        'name': 'create_users_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('email')->unique();
            $table->string('password');
            $table->foreignId('role_id')->constrained();
            $table->rememberToken();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('users');
    }
};'''
    },
    {
        'name': 'create_departments_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('departments', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('code')->unique();
            $table->foreignId('school_id')->constrained();
            $table->text('description')->nullable();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('departments');
    }
};'''
    },
    {
        'name': 'create_department_user_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('department_user', function (Blueprint $table) {
            $table->id();
            $table->foreignId('department_id');
            $table->foreignId('user_id');
            $table->timestamps();

            $table->foreign('department_id')
                  ->references('id')
                  ->on('departments')
                  ->onDelete('cascade');

            $table->foreign('user_id')
                  ->references('id')
                  ->on('users')
                  ->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::dropIfExists('department_user');
    }
};'''
    },
    {
        'name': 'create_lectures_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('lectures', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('code')->unique();
            $table->text('description')->nullable();
            $table->foreignId('department_id')->constrained();
            $table->foreignId('user_id')->constrained();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('lectures');
    }
};'''
    },
    {
        'name': 'create_course_materials_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('course_materials', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();
            $table->string('file_path');
            $table->string('file_type');
            $table->foreignId('lecture_id')->constrained();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('course_materials');
    }
};'''
    },
    {
        'name': 'create_lecture_schedules_table',
        'content': '''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('lecture_schedules', function (Blueprint $table) {
            $table->id();
            $table->foreignId('lecture_id')->constrained();
            $table->dateTime('start_time');
            $table->dateTime('end_time');
            $table->string('venue')->nullable();
            $table->text('notes')->nullable();
            $table->enum('type', ['physical', 'online']);
            $table->string('meeting_link')->nullable();
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('lecture_schedules');
    }
};'''
    }
]

# Ensure database/migrations directory exists
migrations_dir = 'database/migrations'
os.makedirs(migrations_dir, exist_ok=True)

# Generate migration files
for index, migration in enumerate(migrations):
    # Create timestamp with 1 second increment to maintain order
    timestamp = datetime.strptime(base_timestamp, '%Y_%m_%d_%H%M%S')
    adjusted_timestamp = timestamp.timestamp() + index
    new_timestamp = datetime.fromtimestamp(adjusted_timestamp).strftime('%Y_%m_%d_%H%M%S')

    filename = f"{new_timestamp}_{migration['name']}.php"
    filepath = os.path.join(migrations_dir, filename)

    with open(filepath, 'w') as f:
        f.write(migration['content'])

    print(f"Created migration: {filename}")

print("\nAll migrations have been created successfully!")
print("\nNow run:")
print("php artisan migrate:fresh")
