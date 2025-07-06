# app/context_processors.py

def cart_item_count(request):
    """
    A context processor to add the number of items in the cart
    to the context of every template.
    """
    cart = request.session.get('cart', {})
    # We use len(cart) to count the number of unique product types in the cart.
    # If you wanted to count the total number of all items (e.g., 2 of shoe A, 3 of shoe B = 5),
    # you would use: count = sum(cart.values())
    count = len(cart)
    return {'cart_item_count': count}