<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grocery Store</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>Grocery Store</h1>
  <div id="grocery-list">
    <div class="item">
      <span>Apples</span>
      <span>$2.99</span>
      <button class="add-to-cart-btn" data-name="Apples" data-price="2.99">Add to Cart</button>
    </div>
    <div class="item">
      <span>Bananas</span>
      <span>$1.99</span>
      <button class="add-to-cart-btn" data-name="Bananas" data-price="1.99">Add to Cart</button>
    </div>
    <!-- Add more grocery items here -->
  </div>
  <h2>Shopping Cart</h2>
  <div id="shopping-cart">
    <ul id="cart-list"></ul>
    <div id="total">Total: $0.00</div>
  </div>
  <script src="script.js"></script>
</body>
</html>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
}

h1, h2 {
  text-align: center;
}

#grocery-list {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.item {
  margin-bottom: 10px;
}

.add-to-cart-btn {
  margin-left: 10px;
}

#shopping-cart {
  margin-top: 50px;
}

#cart-list {
  list-style: none;
  padding: 0;
}

.cart-item {
  display: flex;
  justify-content: space-between;
}

#total {
  text-align: right;
}
document.addEventListener('DOMContentLoaded', function() {
  const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
  const cartList = document.getElementById('cart-list');
  const totalElement = document.getElementById('total');
  let total = 0;

  addToCartButtons.forEach(button => {
    button.addEventListener('click', function() {
      const itemName = button.dataset.name;
      const itemPrice = parseFloat(button.dataset.price);
      total += itemPrice;
      totalElement.textContent = `Total: $${total.toFixed(2)}`;
      const listItem = document.createElement('li');
      listItem.classList.add('cart-item');
      listItem.innerHTML = `
        <span>${itemName}</span>
        <span>$${itemPrice.toFixed(2)}</span>
      `;
      cartList.appendChild(listItem);
    });
  });
});
