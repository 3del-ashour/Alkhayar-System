## Alkhayar Internal Communication & Logistics System

This application centralizes messaging, task tracking, and shipment management for Alkhayar Company. It is built on top of Laravel with Jetstream and ships with Arabic localisation and RTL-friendly views.

### Installation

```
# from project root
composer install

cp .env.example .env
php artisan key:generate

php artisan migrate        # or: php artisan migrate:fresh
php artisan db:seed --class=FixedUsersSeeder

npm install
npm run build              # or: npm run dev (in a second terminal)

php artisan cache:clear && php artisan config:clear && php artisan view:clear
php artisan serve          # open http://127.0.0.1:8000
```
