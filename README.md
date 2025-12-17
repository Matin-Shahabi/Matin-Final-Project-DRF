# 🛒 Custom Online Shop – Django & DRF Final Project

## 📌 Project Overview

**Custom Online Shop** is a full-featured e-commerce backend built with **Django** and **Django REST Framework**.
The project is designed as a **real-world, scalable online marketplace** supporting multiple sellers, shared products across stores, secure authentication, and a fully snapshot-based order system.

This project is developed as the **Final Project for Python Bootcamp 134** and follows clean architecture, proper database normalization, and production-ready design principles.

---

## 🚀 Key Features

### 👥 Users & Authentication

* OTP-based user registration (email or phone)
* JWT authentication for protected endpoints
* Role-based access control:

  * Guest
  * Customer
  * Seller
  * Admin
* User profile management
* Multiple user addresses (shipping & billing)

---

### 🏬 Sellers & Stores

* Seller registration and store creation
* Each seller can manage one or more stores
* Store details:

  * Name, logo, rating
  * Sales count
  * Total product count
* Sellers can manage products, pricing, and stock per store

---

### 📦 Products & Categories

* Hierarchical categories (parent / child categories)
* Products can belong to **multiple stores**
* Store-specific product configuration via `ProductStore`:

  * Price per store
  * Discount per store
* Product listing supports:

  * Pagination
  * Sorting (price, rating, newest, best-selling)

---

### 🛒 Cart System

* Each authenticated user has an automatic cart
* Cart items are linked to **store-specific products**
* Supported actions:

  * Add to cart
  * Update quantity
  * Remove item
  * Clear cart

---

### 💸 Coupons & Discounts

* Coupon system with:

  * Expiration date
  * Usage limits
* Coupon validation during checkout
* Coupon data is **snapshotted** into the order

---

### 📑 Orders (Snapshot-Based)

* Cart is converted into an immutable order
* Orders support multiple stores in a single checkout
* Order snapshots ensure historical accuracy:

  * Product price snapshot
  * Discount snapshot
  * Final price snapshot
* Order statuses:

  * Pending
  * Paid
  * Shipped
  * Delivered
  * Cancelled
* Full order status history tracking

---

### 💳 Payments

* One payment per order
* Payment records include:

  * Amount
  * Payment type
  * Date & time
* Protection against duplicate payments

---

### ⭐ Reviews & Ratings

* Users can review products **only after purchase**
* One review per user per product
* Public product ratings and comments

---

### ❤️ Wishlist

* Add or remove products from wishlist
* View saved wishlist items

---

## 🧠 System Design Principles

### 🔒 Snapshot-Based Financial Data

To ensure financial and historical integrity:

* Orders do **NOT** depend on live product or discount data
* All prices and discounts are snapshotted at checkout time

### 🔁 Many-to-Many Product–Store Relationship

* A product can be sold by multiple stores
* A store can sell multiple products
* Implemented using a dedicated `ProductStore` pivot table

### 🔐 Access Control

* Customers manage carts, orders, reviews, and wishlists
* Sellers manage stores and products
* Admins oversee the entire system

---

## 🗂 Database Architecture (High Level)

Main entities:

* User
* Address
* Store
* Category
* Product
* ProductStore
* Cart / CartItem
* Order / OrderItem
* OrderStatusHistory
* Payment
* Coupon
* Review
* Wishlist

The database schema is fully normalized and designed for scalability.

---

## 🛠 Technology Stack

* **Python 3**
* **Django**
* **Django REST Framework**
* **PostgreSQL**
* **Docker & Docker Compose**
* **JWT Authentication**
* **Git (Version Control)**

---


## 📁 Project Structure (Planned)

```
custom_shop/
├── users/
├── stores/
├── products/
├── cart/
├── orders/
├── payments/
├── reviews/
├── wishlist/
├── coupons/
└── core/
```

---

## 👨‍🏫 Teaching Team

* امیرحسین چگونیان
* رضا غلامی
* سینا ملکی
* رضا یادگاری
* یاس قطبی‌زاده

---
