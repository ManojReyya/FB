# FBAIS API Documentation

## Overview

This document provides comprehensive documentation for all API endpoints in the FBAIS (Food Business AI System). All endpoints return JSON responses and use RESTful conventions.

**Base URL:** `http://localhost:5000`

---

## Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [Profitability Prediction APIs](#profitability-prediction-apis)
3. [Customer Persona APIs](#customer-persona-apis)
4. [Recipe & Inventory APIs](#recipe--inventory-apis)
5. [Waste Tracking APIs](#waste-tracking-apis)
6. [System APIs](#system-apis)

---

## Authentication APIs

### Register User

**Endpoint:** `POST /api/register`

**Description:** Creates a new user account.

**CSRF Protection:** Exempt

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "business_name": "John's Restaurant",
  "password": "SecurePass123"
}
```

**Validation Rules:**
- `full_name`: Required, max 100 characters
- `email`: Required, valid email format, max 255 characters
- `business_name`: Optional, max 200 characters
- `password`: Required, min 8 characters, must contain uppercase, lowercase, and numbers

**Success Response (200):**
```json
{
  "success": true,
  "message": "Account created"
}
```

**Error Responses:**
- **400 Bad Request:** Missing fields or validation failure
- **409 Conflict:** Email already registered

---

### Login User

**Endpoint:** `POST /api/login`

**Description:** Authenticates a user and creates a session.

**CSRF Protection:** Exempt

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Error Responses:**
- **400 Bad Request:** Missing email or password
- **401 Unauthorized:** Invalid credentials

**Side Effects:**
- Creates session with `user_id`, `user_name`, `user_email`
- Updates `last_login` timestamp in database

---

### Logout User

**Endpoint:** `GET /api/logout` or `GET /logout`

**Description:** Logs out the current user and clears session.

**Authentication:** Not required

**Success Response:**
- Redirects to landing page

---

### Update Profile

**Endpoint:** `POST /api/update-profile`

**Description:** Updates user profile information.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "John Updated",
  "business_name": "John's Updated Restaurant",
  "phone": "9876543210"
}
```

**Validation:**
- `name`: Required, max 100 characters
- `business_name`: Optional, max 200 characters
- `phone`: Optional, numeric validation

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated"
}
```

**Error Responses:**
- **400 Bad Request:** Missing name
- **401 Unauthorized:** Not logged in
- **500 Internal Server Error:** Database error

---

## Profitability Prediction APIs

### Get Restaurant Configuration

**Endpoint:** `GET /api/restaurant-config`

**Description:** Returns available cities, cuisines, and location types for profit prediction.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "cities": [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", ...
  ],
  "cuisines": [
    "North Indian", "South Indian", "Chinese", "Continental", ...
  ],
  "location_types": [
    "Street", "Market", "Mall", "Standalone", "Food Court", "Airport"
  ]
}
```

---

### Predict Profit

**Endpoint:** `POST /api/predict-profit`

**Description:** Predicts monthly profit and risk level for a restaurant configuration.

**Authentication:** Recommended (not enforced)

**CSRF Protection:** Exempt

**Request Body:**
```json
{
  "city": "Mumbai",
  "location_type": "Mall",
  "cuisine_type": "North Indian",
  "seating_capacity": 50,
  "avg_table_size": 4,
  "parking_available": 1,
  "home_delivery": 1,
  "operating_hours": 12,
  "days_open_per_week": 7,
  "years_in_business": 2,
  "avg_daily_customers": 150,
  "customer_rating": 4.2,
  "online_orders_pct": 30,
  "avg_order_value": 450,
  "staff_count": 12,
  "chef_experience_years": 8,
  "food_quality_score": 8.0,
  "service_quality_score": 7.5,
  "ambiance_score": 8.0,
  "competitors_nearby": 5,
  "population_density": 8000,
  "foot_traffic": 2000,
  "rent_monthly": 120000,
  "staff_salary_monthly": 240000,
  "marketing_budget": 20000,
  "utility_cost": 15000,
  "food_cost_pct": 32
}
```

**Field Descriptions:**
- **Binary fields:** `parking_available`, `home_delivery` (0 or 1)
- **Percentages:** `online_orders_pct`, `food_cost_pct` (0-100)
- **Scores:** `food_quality_score`, `service_quality_score`, `ambiance_score` (0-10)
- **Financial:** All costs in ₹ (Rupees)

**Success Response (200):**
```json
{
  "success": true,
  "predicted_profit": 185234.56,
  "monthly_revenue": 675000.00,
  "monthly_costs": 489765.44,
  "profit_margin": 27.44,
  "risk_level": "Low",
  "recommendations": [
    "Your profit margin is healthy. Focus on maintaining quality.",
    "Consider expanding marketing budget to increase customer base.",
    "Monitor food costs to maintain current margins."
  ],
  "feature_importance": {
    "avg_daily_customers": 0.342,
    "avg_order_value": 0.198,
    "rent_monthly": 0.156,
    "staff_salary_monthly": 0.124,
    "customer_rating": 0.089,
    ...
  }
}
```

**Error Response (500):**
```json
{
  "success": false,
  "error": "Prediction failed"
}
```

---

### Get Feature Importance

**Endpoint:** `GET /api/feature-importance`

**Description:** Returns the importance scores of all features used in profit prediction.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "success": true,
  "feature_importance": {
    "avg_daily_customers": 0.342,
    "avg_order_value": 0.198,
    "rent_monthly": 0.156,
    ...
  }
}
```

---

## Customer Persona APIs

### Identify Customer Persona

**Endpoint:** `POST /api/customer/identify`

**Description:** Identifies customer persona using hybrid ML + rule-based system.

**Authentication:** Recommended

**CSRF Protection:** Exempt

**Request Body:**
```json
{
  "time": 19,
  "budget_level": "high",
  "food_type": "dine_in",
  "occasion": "celebration",
  "customer_type": "family",
  "delivery_preference": "no_delivery",
  "payment_method": "card"
}
```

**Field Options:**
- **time:** 0-23 (hour of day)
- **budget_level:** "low", "medium", "high", "premium"
- **food_type:** "street_food", "home_delivery", "dine_in", "catering", "health_conscious"
- **occasion:** "daily_meal", "casual_outing", "celebration", "event"
- **customer_type:** "student", "working_professional", "family", "food_enthusiast", "event_planner"
- **delivery_preference:** "no_delivery", "app_delivery", "self_pickup"
- **payment_method:** "cash", "upi", "card", "paytm", "online_transfer"

**Success Response (200):**
```json
{
  "success": true,
  "persona": "fine_dining_premium",
  "persona_name": "Fine Dining & Premium Restaurants",
  "confidence": 0.87,
  "description": "High-end dining establishments with premium ingredients...",
  "characteristics": {
    "price_range": "₹800-3000+",
    "avg_spending": "₹1200",
    "primary_channels": ["Instagram", "Events", "Premium Food Apps"],
    "peak_times": ["Evenings (6pm-11pm)", "Weekends"],
    "payment_preferences": ["Card", "UPI", "Online Transfer"]
  },
  "recommendations": {
    "marketing": "Focus on experiential marketing and social media presence",
    "pricing": "Premium pricing justified by quality and ambiance",
    "service": "Highly trained staff, personalized service"
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Missing required fields"
}
```

---

### Get All Personas

**Endpoint:** `GET /api/customer/personas`

**Description:** Returns definitions of all 7 customer personas.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "success": true,
  "personas": [
    {
      "id": "street_food",
      "name": "Street Food & Quick Bites",
      "price_range": "₹50-150",
      "description": "...",
      "characteristics": { ... },
      "marketing_strategies": [ ... ]
    },
    ...
  ]
}
```

---

### Get Persona Statistics

**Endpoint:** `GET /api/customer/stats`

**Description:** Returns statistics about customer personas.

**Authentication:** Recommended

**Success Response (200):**
```json
{
  "success": true,
  "total_personas": 7,
  "categories": {
    "budget_focused": 2,
    "experience_focused": 3,
    "convenience_focused": 2
  }
}
```

---

## Recipe & Inventory APIs

### Search Recipes

**Endpoint:** `GET /api/recipes/search?q={query}`

**Description:** Searches recipes by name from 16,525+ Indian recipes.

**Authentication:** Recommended

**Query Parameters:**
- `q` (required): Search query string

**Success Response (200):**
```json
{
  "success": true,
  "count": 15,
  "recipes": [
    {
      "id": 1234,
      "name": "Butter Chicken",
      "cuisine": "North Indian",
      "diet": "Non-Vegetarian",
      "prep_time": 30,
      "cook_time": 45,
      "servings": 4
    },
    ...
  ]
}
```

---

### Get Recipe Details

**Endpoint:** `GET /api/recipes/{recipe_id}`

**Description:** Returns detailed information about a specific recipe.

**Authentication:** Recommended

**Success Response (200):**
```json
{
  "success": true,
  "recipe": {
    "id": 1234,
    "name": "Butter Chicken",
    "cuisine": "North Indian",
    "diet": "Non-Vegetarian",
    "prep_time": 30,
    "cook_time": 45,
    "servings": 4,
    "ingredients": [
      "500g chicken",
      "200ml cream",
      "2 tbsp butter",
      ...
    ],
    "instructions": "..."
  }
}
```

---

### Scale Recipe

**Endpoint:** `POST /api/recipes/{recipe_id}/scale`

**Description:** Scales recipe ingredients for a different number of servings.

**Authentication:** Recommended

**Request Body:**
```json
{
  "target_servings": 20
}
```

**Success Response (200):**
```json
{
  "success": true,
  "original_servings": 4,
  "target_servings": 20,
  "scaling_factor": 5.0,
  "scaled_ingredients": [
    "2500g chicken",
    "1000ml cream",
    "10 tbsp butter",
    ...
  ]
}
```

---

### Get Recipe Statistics

**Endpoint:** `GET /api/recipes/stats`

**Description:** Returns statistics about the recipe database.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "success": true,
  "total_recipes": 16525,
  "cuisines": {
    "North Indian": 4523,
    "South Indian": 3876,
    "Chinese": 2134,
    ...
  },
  "diet_types": {
    "Vegetarian": 9234,
    "Non-Vegetarian": 6128,
    "Vegan": 1163
  }
}
```

---

## Waste Tracking APIs

### Add Waste Entry

**Endpoint:** `POST /api/waste/add`

**Description:** Records a food waste entry.

**Authentication:** Required

**CSRF Protection:** Exempt

**Request Body:**
```json
{
  "itemName": "Tomatoes",
  "category": "Vegetables",
  "quantity": 2.5,
  "unit": "kg",
  "date": "2024-01-15",
  "cost": 150.00,
  "notes": "Spoiled due to excess stock"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Waste entry added",
  "entry_id": 42
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Missing required fields"
}
```

---

### Get Waste Entries

**Endpoint:** `GET /api/waste/entries`

**Description:** Returns all waste entries for the logged-in user.

**Authentication:** Required

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `category` (optional): Filter by category

**Success Response (200):**
```json
{
  "success": true,
  "count": 25,
  "entries": [
    {
      "id": 42,
      "item_name": "Tomatoes",
      "category": "Vegetables",
      "quantity": 2.5,
      "unit": "kg",
      "date": "2024-01-15",
      "cost": 150.00,
      "notes": "Spoiled due to excess stock"
    },
    ...
  ]
}
```

---

### Get Waste Categories

**Endpoint:** `GET /api/waste/categories`

**Description:** Returns available waste categories.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "success": true,
  "categories": [
    "Vegetables",
    "Fruits",
    "Meat",
    "Dairy",
    "Grains",
    "Prepared Food",
    "Other"
  ]
}
```

---

### Get Waste Analytics

**Endpoint:** `GET /api/waste/analytics`

**Description:** Returns waste analytics and statistics.

**Authentication:** Required

**Query Parameters:**
- `period` (optional): "week", "month", "year", "all" (default: "all")

**Success Response (200):**
```json
{
  "success": true,
  "total_waste_cost": 15480.00,
  "weekly_waste_cost": 1250.00,
  "category_breakdown": {
    "Vegetables": 4520.00,
    "Meat": 6200.00,
    "Dairy": 2340.00,
    "Prepared Food": 2420.00
  },
  "trend": [
    {"date": "2024-01-01", "cost": 280.00},
    {"date": "2024-01-02", "cost": 320.00},
    ...
  ],
  "top_waste_items": [
    {"item": "Tomatoes", "cost": 850.00, "occurrences": 5},
    {"item": "Lettuce", "cost": 640.00, "occurrences": 4}
  ]
}
```

---

### Delete Waste Entry

**Endpoint:** `DELETE /api/waste/{entry_id}`

**Description:** Deletes a specific waste entry.

**Authentication:** Required

**Success Response (200):**
```json
{
  "success": true,
  "message": "Waste entry deleted"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Entry not found"
}
```

---

## System APIs

### Health Check

**Endpoint:** `GET /health`

**Description:** Returns system health status.

**Authentication:** Not required

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Error Handling

All API endpoints follow consistent error response format:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

### Common HTTP Status Codes:
- **200 OK:** Request successful
- **400 Bad Request:** Invalid input or missing required fields
- **401 Unauthorized:** Authentication required or invalid credentials
- **404 Not Found:** Resource not found
- **409 Conflict:** Resource already exists (e.g., duplicate email)
- **500 Internal Server Error:** Server-side error

---

## Security Notes

1. **CSRF Protection:** Most endpoints use CSRF tokens except those marked as exempt (login, register, ML prediction APIs)
2. **Authentication:** Session-based authentication with secure cookies
3. **Password Security:** Bcrypt hashing with configurable salt rounds
4. **Input Sanitization:** All inputs are sanitized to prevent XSS and SQL injection
5. **Rate Limiting:** Consider implementing rate limiting for production use

---

## Rate Limiting (Recommended for Production)

While not currently implemented, production deployments should consider:
- **Authentication endpoints:** 5 requests per minute
- **Prediction endpoints:** 20 requests per minute
- **Search endpoints:** 30 requests per minute
- **CRUD operations:** 60 requests per minute

---

## Integration Examples

### Python Example (using requests):
```python
import requests

# Login
login_data = {
    "email": "john@example.com",
    "password": "SecurePass123"
}
session = requests.Session()
response = session.post("http://localhost:5000/api/login", json=login_data)

# Predict profit
profit_data = {
    "city": "Mumbai",
    "cuisine_type": "North Indian",
    "avg_daily_customers": 150,
    # ... other fields
}
response = session.post("http://localhost:5000/api/predict-profit", json=profit_data)
result = response.json()
print(f"Predicted Profit: ₹{result['predicted_profit']}")
```

### JavaScript Example (using fetch):
```javascript
// Login
const loginData = {
  email: 'john@example.com',
  password: 'SecurePass123'
};

fetch('http://localhost:5000/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(loginData),
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data));

// Identify persona
const personaData = {
  time: 19,
  budget_level: 'high',
  food_type: 'dine_in',
  occasion: 'celebration'
};

fetch('http://localhost:5000/api/customer/identify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(personaData),
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log('Persona:', data.persona_name));
```

---

## API Versioning

**Current Version:** v1 (implied, not in URL)

Future versions will use URL versioning:
- `/api/v1/predict-profit`
- `/api/v2/predict-profit`

---

## Support & Questions

For API-related questions or bug reports, refer to the main README.md or contact the development team.

---

*Last Updated: January 2024*
