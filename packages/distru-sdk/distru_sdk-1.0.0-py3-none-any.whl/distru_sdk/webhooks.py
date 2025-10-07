"""Webhook handling for Distru API events."""

from typing import Any, Callable, Dict, List, Optional


class WebhookEvent:
    """Represents a webhook event from Distru.

    Attributes:
        type: Event type (ORDER, INVOICE, PURCHASE, etc.)
        id: Entity ID
        before_changes: Entity state before change (empty dict for CREATE)
        after_changes: Entity state after change (empty dict for DELETE)
        products_by_id: Product reference data (optional)
        order_items_by_id: Order item reference data (optional)
        batches_by_id: Batch reference data (optional)
        packages_by_id: Package reference data (optional)
    """

    def __init__(self, payload: Dict[str, Any]) -> None:
        """Initialize webhook event from payload.

        Args:
            payload: Raw webhook payload
        """
        self.type = payload.get("type", "")
        self.id = payload.get("id", "")
        self.before_changes = payload.get("before_changes", {})
        self.after_changes = payload.get("after_changes", {})
        self.products_by_id = payload.get("products_by_id", {})
        self.order_items_by_id = payload.get("order_items_by_id", {})
        self.batches_by_id = payload.get("batches_by_id", {})
        self.packages_by_id = payload.get("packages_by_id", {})
        self._raw_payload = payload

    @property
    def action(self) -> str:
        """Determine the action type based on before/after changes.

        Returns:
            'created', 'updated', or 'deleted'
        """
        if not self.before_changes:
            return "created"
        elif not self.after_changes:
            return "deleted"
        else:
            return "updated"

    def is_created(self) -> bool:
        """Check if this is a create event."""
        return self.action == "created"

    def is_updated(self) -> bool:
        """Check if this is an update event."""
        return self.action == "updated"

    def is_deleted(self) -> bool:
        """Check if this is a delete event."""
        return self.action == "deleted"

    def get_changed_fields(self) -> List[str]:
        """Get list of fields that changed (for update events).

        Returns:
            List of field names that changed
        """
        if not self.is_updated():
            return []

        changed = []
        for key in self.after_changes.keys():
            if key in self.before_changes:
                if self.before_changes[key] != self.after_changes[key]:
                    changed.append(key)
            else:
                changed.append(key)

        return changed

    def __repr__(self) -> str:
        """Return string representation of event."""
        return f"WebhookEvent(type={self.type!r}, id={self.id!r}, action={self.action!r})"


class WebhookHandler:
    """Handler for processing Distru webhook events.

    Example:
        >>> handler = WebhookHandler()
        >>>
        >>> @handler.on('ORDER')
        >>> def handle_order(event):
        ...     if event.is_created():
        ...         print(f"New order: {event.after_changes['order_number']}")
        >>>
        >>> # In your web framework
        >>> payload = request.get_json()
        >>> handler.process(payload)
    """

    def __init__(self) -> None:
        """Initialize webhook handler."""
        self._handlers: Dict[str, List[Callable[[WebhookEvent], None]]] = {}
        self._global_handlers: List[Callable[[WebhookEvent], None]] = []

    def on(self, event_type: str) -> Callable:
        """Register a handler for a specific event type.

        Args:
            event_type: Event type to handle (ORDER, INVOICE, PURCHASE, etc.)

        Returns:
            Decorator function

        Example:
            >>> @handler.on('ORDER')
            >>> def handle_order(event):
            ...     print(f"Order event: {event.action}")
        """

        def decorator(func: Callable[[WebhookEvent], None]) -> Callable[[WebhookEvent], None]:
            self.register(event_type, func)
            return func

        return decorator

    def on_any(self) -> Callable:
        """Register a handler for all event types.

        Returns:
            Decorator function

        Example:
            >>> @handler.on_any()
            >>> def handle_all(event):
            ...     print(f"Event: {event.type} - {event.action}")
        """

        def decorator(func: Callable[[WebhookEvent], None]) -> Callable[[WebhookEvent], None]:
            self.register_global(func)
            return func

        return decorator

    def register(self, event_type: str, handler: Callable[[WebhookEvent], None]) -> None:
        """Register a handler function for an event type.

        Args:
            event_type: Event type to handle
            handler: Handler function that takes WebhookEvent
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def register_global(self, handler: Callable[[WebhookEvent], None]) -> None:
        """Register a handler for all event types.

        Args:
            handler: Handler function that takes WebhookEvent
        """
        self._global_handlers.append(handler)

    def process(self, payload: Dict[str, Any]) -> None:
        """Process a webhook payload.

        Args:
            payload: Webhook payload dictionary

        Raises:
            ValueError: If payload is invalid

        Example:
            >>> payload = request.get_json()
            >>> handler.process(payload)
        """
        # Validate payload
        if not isinstance(payload, dict):
            raise ValueError("Webhook payload must be a dictionary")

        if "type" not in payload:
            raise ValueError("Webhook payload missing 'type' field")

        # Create event object
        event = WebhookEvent(payload)

        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue processing other handlers
                print(f"Error in global webhook handler: {e}")

        # Call specific handlers
        event_type = event.type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but continue processing other handlers
                    print(f"Error in {event_type} webhook handler: {e}")

    def has_handler(self, event_type: str) -> bool:
        """Check if there are handlers registered for an event type.

        Args:
            event_type: Event type to check

        Returns:
            True if handlers are registered
        """
        return event_type in self._handlers and len(self._handlers[event_type]) > 0

    def clear_handlers(self, event_type: Optional[str] = None) -> None:
        """Clear registered handlers.

        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type is None:
            self._handlers.clear()
            self._global_handlers.clear()
        elif event_type in self._handlers:
            del self._handlers[event_type]


# Flask integration example
def create_flask_webhook_handler(
    handler: WebhookHandler, route: str = "/webhooks"
) -> Callable:
    """Create a Flask webhook endpoint.

    Args:
        handler: WebhookHandler instance
        route: Route path for webhook endpoint

    Returns:
        Flask route function

    Example:
        >>> from flask import Flask, request
        >>> app = Flask(__name__)
        >>>
        >>> handler = WebhookHandler()
        >>> webhook_view = create_flask_webhook_handler(handler)
        >>>
        >>> app.route('/webhooks', methods=['POST'])(webhook_view)
    """
    from flask import request, jsonify

    def webhook_view():
        try:
            payload = request.get_json()
            handler.process(payload)
            return jsonify({"status": "ok"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500

    return webhook_view


# FastAPI integration example
def create_fastapi_webhook_handler(handler: WebhookHandler) -> Callable:
    """Create a FastAPI webhook endpoint.

    Args:
        handler: WebhookHandler instance

    Returns:
        FastAPI route function

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>>
        >>> handler = WebhookHandler()
        >>> webhook_route = create_fastapi_webhook_handler(handler)
        >>>
        >>> @app.post("/webhooks")
        >>> async def webhook_endpoint(payload: dict):
        >>>     return webhook_route(payload)
    """

    async def webhook_route(payload: Dict[str, Any]) -> Dict[str, str]:
        try:
            handler.process(payload)
            return {"status": "ok"}
        except ValueError as e:
            return {"error": str(e)}
        except Exception:
            return {"error": "Internal server error"}

    return webhook_route
