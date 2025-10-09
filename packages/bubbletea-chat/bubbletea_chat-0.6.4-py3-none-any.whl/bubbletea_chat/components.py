"""
BubbleTea UI Components
"""

from typing import List, Literal, Optional, Union
from pydantic import BaseModel


class Text(BaseModel):
    """Plain text message component"""

    type: Literal["text"] = "text"
    content: str

    def __init__(self, content: str):
        super().__init__(content=content)


class Image(BaseModel):
    """Image display component"""

    type: Literal["image"] = "image"
    url: str
    alt: Optional[str] = None
    content: Optional[str] = None

    def __init__(
        self, url: str, alt: Optional[str] = None, content: Optional[str] = None
    ):
        super().__init__(url=url, alt=alt, content=content)


class Markdown(BaseModel):
    """Rich text with markdown formatting"""

    type: Literal["markdown"] = "markdown"
    content: str

    def __init__(self, content: str):
        super().__init__(content=content)


class Card(BaseModel):
    """Interactive card with image and text"""

    type: Literal["card"] = "card"
    image: Image
    text: Optional[str] = None
    markdown: Optional[Markdown] = None
    card_value: Optional[str] = None

    def __init__(
        self,
        image: Image,
        text: Optional[str] = None,
        markdown: Optional[Markdown] = None,
        card_value: Optional[str] = None,
    ):
        super().__init__(
            image=image, text=text, markdown=markdown, card_value=card_value
        )


class Cards(BaseModel):
    """Grid layout for multiple cards"""

    type: Literal["cards"] = "cards"
    orient: Literal["wide", "tall"] = "wide"
    cards: List[Card]

    def __init__(self, cards: List[Card], orient: Literal["wide", "tall"] = "wide"):
        super().__init__(cards=cards, orient=orient)


class Done(BaseModel):
    """Stream completion signal"""

    type: Literal["done"] = "done"


class Pill(BaseModel):
    """Clickable pill button"""

    type: Literal["pill"] = "pill"
    text: str
    pill_value: Optional[str] = None

    def __init__(self, text: str, pill_value: Optional[str] = None):
        super().__init__(text=text, pill_value=pill_value)


class Pills(BaseModel):
    """Group of pill buttons"""

    type: Literal["pills"] = "pills"
    pills: List[Pill]

    def __init__(self, pills: List[Pill]):
        super().__init__(pills=pills)


class Video(BaseModel):
    """Video display component"""

    type: Literal["video"] = "video"
    url: str

    def __init__(self, url: str):
        super().__init__(url=url)


class Block(BaseModel):
    """Loading indicator"""

    type: Literal["block"] = "block"
    timeout: int = 60

    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)


class Error(BaseModel):
    """Error message display"""

    type: Literal["error"] = "error"
    title: str
    description: Optional[str] = None
    code: Optional[str] = None

    def __init__(
        self, title: str, description: Optional[str] = None, code: Optional[str] = None
    ):
        super().__init__(title=title, description=description, code=code)


class PaymentRequest(BaseModel):
    """Payment request component"""

    type: Literal["payment_request"] = "payment_request"
    amount: float
    note: Optional[str] = None

    def __init__(self, amount: float, note: Optional[str] = None):
        super().__init__(amount=amount, note=note)


Component = Union[
    Text, Image, Markdown, Card, Cards, Done, Pill, Pills, Video, Block, Error, PaymentRequest
]


class BaseComponent(BaseModel):
    """Internal wrapper for components with metadata"""

    thread_id: Optional[str] = None
    payload: List[Component]

    def __init__(
        self,
        payload: Union[Component, List[Component]],
        thread_id: Optional[str] = None,
    ):
        if not isinstance(payload, list):
            payload = [payload]
        super().__init__(payload=payload, thread_id=thread_id)
