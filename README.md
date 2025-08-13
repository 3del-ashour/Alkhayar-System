## Alkhayar Internal Communication & Logistics System

This application centralizes messaging, task tracking, and shipment management for Alkhayar Company. It is built on top of Laravel with Jetstream and ships with Arabic localisation and RTL-friendly views.

### Installation

```
composer install
npm install
cp .env.example .env
php artisan key:generate
php artisan migrate
npm run build
```

Run the development server with:

```
php artisan serve
```

### Testing

```
php artisan test
```
