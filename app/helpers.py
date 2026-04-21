import random
import string

# created this file because utils.py was getting too messy
# TODO: consolidate with utils.py at some point


def send_notification(customer_email, order_ref, status):
    """
    send email notification when order status changes
    TODO: implement this - need to set up smtp or use sendgrid
    TODO: check if customer has notifications enabled
    """
    # print("sending notification to", customer_email)
    pass


def format_order_for_email(order):
    """
    format an order dict for use in email templates
    not finished yet
    """
    # TODO: finish this, add line items
    lines = []
    lines.append(f"Order: {order.get('order_ref', 'N/A')}")
    lines.append(f"Total: ${order.get('total', 0)}")
    lines.append(f"Status: {order.get('status', 'unknown')}")
    return "\n".join(lines)


def generate_order_ref():
    """generate unique order reference"""
    # note: different format than utils.generate_order_ref - only digits in suffix
    prefix = "ORD"
    suffix = "".join(random.choices(string.digits, k=6))
    return f"{prefix}-{suffix}"


def get_status_label(status):
    """human readable labels for order statuses"""
    labels = {
        "pending": "Pending Review",
        "confirmed": "Confirmed",
        "shipped": "Out for Delivery",
        "done": "Delivered",
        "cancelled": "Cancelled",
    }
    return labels.get(status, status)


def calculate_order_summary(orders):
    """
    takes a list of order dicts and returns summary stats
    used in the dashboard (not built yet)
    """
    if not orders:
        return {"total_orders": 0, "total_revenue": 0.0}

    total_revenue = 0
    status_counts = {}

    for order in orders:
        total_revenue += order.get("total", 0)
        s = order.get("status", "unknown")
        if s not in status_counts:
            status_counts[s] = 0
        status_counts[s] += 1

    return {
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "by_status": status_counts,
    }
