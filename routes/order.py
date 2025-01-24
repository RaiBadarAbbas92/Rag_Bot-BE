from fastapi import FastAPI, File, UploadFile, Form, APIRouter
from sqlmodel import SQLModel, create_engine, Session, Field , select
from pydantic import BaseModel
from typing import Optional
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

order_router = APIRouter(prefix="/order")

app = FastAPI()

class Order(BaseModel):
    username: str
    email: str
    challenge_type: str
    account_size: str
    platform: str
    payment_method: str
    txid: str
    img: UploadFile

class OrderModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    challenge_type: str
    account_size: str
    platform: str
    payment_method: str
    txid: str
    img: bytes

DATABASE_URL = "postgresql://neondb_owner:FCiveKQU8qE5@ep-small-dust-a8qjgte2.eastus2.azure.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)
def send_email(to_email, subject, body):
    from_email = "raibadar37218@gmail.com"
    from_password = "aqojinprzpqfhlxk"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())

@order_router.post("/order")
async def create_order(
    username: str = Form(...),
    email: str = Form(...),
    challenge_type: str = Form(...),
    account_size: str = Form(...),
    platform: str = Form(...),
    payment_method: str = Form(...),
    txid: str = Form(...),
    img: UploadFile = File(...)
):
    order = OrderModel(
        username=username,
        email=email,
        challenge_type=challenge_type,
        account_size=account_size,
        platform=platform,
        payment_method=payment_method,
        txid=txid,
        img=await img.read()
    )
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)
    
    # Send email notification
    subject = "Order Created Successfully"
    body = f"Dear {username},\n\nYour order has been created successfully.\n\nOrder ID: FDH{order.id}\n\nThank you for your purchase!"
    send_email(email, subject, body)
    
    return {"id": f"FDH{order.id}", "message": "Order created successfully"}
@order_router.get("/order/{order_id}")
async def get_order(order_id: int):
    with Session(engine) as session:
        order = session.get(OrderModel, order_id)
        if order is None:
            return {"error": "Order not found"}
        return {
            "id": f"FDH{order.id}",
            "username": order.username,
            "email": order.email,
            "challenge_type": order.challenge_type,
            "account_size": order.account_size,
            "platform": order.platform,
            "payment_method": order.payment_method,
            "txid": order.txid,
            "img": base64.b64encode(order.img).decode('utf-8')
        }

@order_router.get("/orders")
async def get_all_orders():
                with Session(engine) as session:
                    orders = session.exec(select(OrderModel)).all()
                    return [
                        {
                            "id": f"FDH{order.id}",
                            "username": order.username,
                            "email": order.email,
                            "challenge_type": order.challenge_type,
                            "account_size": order.account_size,
                            "platform": order.platform,
                            "payment_method": order.payment_method,
                            "txid": order.txid,
                            "img": base64.b64encode(order.img).decode('utf-8')
                        }
                        for order in orders
                    ]


class CompleteOrderModel(SQLModel, table=True):
                        id: Optional[int] = Field(default=None, primary_key=True)
                        order_id: int = Field(foreign_key="ordermodel.id")
                        server: str
                        platform_login: str
                        platform_password: str

SQLModel.metadata.create_all(engine)
@order_router.post("/complete_order/{order_id}")
async def complete_order(
                        order_id: int,
                        server: str = Form(...),
                        platform_login: str = Form(...),
                        platform_password: str = Form(...)
                    ):
                        with Session(engine) as session:
                            order = session.get(OrderModel, order_id)
                            if order is None:
                                return {"error": "Order not found"}

                            complete_order = CompleteOrderModel(
                                order_id=order_id,
                                server=server,
                                platform_login=platform_login,
                                platform_password=platform_password
                            )
                            session.add(complete_order)
                            session.commit()
                            session.refresh(complete_order)

                        return {"message": "Order completed successfully", "complete_order_id": complete_order.id}


@order_router.get("/completed_orders")
async def get_all_completed_orders():
                            with Session(engine) as session:
                                completed_orders = session.exec(select(CompleteOrderModel)).all()
                                return [
                                    {
                                        "complete_order_id": completed_order.id,
                                        "order_id": f"FDH{completed_order.order_id}",
                                        "server": completed_order.server,
                                        "platform_login": completed_order.platform_login,
                                        "platform_password": completed_order.platform_password
                                    }
                                    for completed_order in completed_orders]
@order_router.get("/order_ids")
async def get_order_ids():
    with Session(engine) as session:
        orders = session.exec(select(OrderModel.id, OrderModel.account_size, OrderModel.username)).all()
        return [{"order_id": f"FDH{order.id}", "balance": order.account_size, "username": order.username} for order in orders]

@order_router.get("/account_detail/{order_id}")
async def get_account_detail(order_id: int):
            with Session(engine) as session:
                order = session.get(OrderModel, order_id)
                if order is None:
                    return {"error": "Order not found"}
                
                order_detail = {
                    "order_id": f"FDH{order.id}",
                    "challenge_type": order.challenge_type,
                    "account_size": order.account_size,
                    "platform": order.platform,
                    "username": order.username
                }
                
                completed_order = session.exec(select(CompleteOrderModel).where(CompleteOrderModel.order_id == order_id)).first()
                if completed_order:
                    order_detail.update({
                        "server": completed_order.server,
                        "platform_login": completed_order.platform_login,
                        "platform_password": completed_order.platform_password
                    })
                
                return order_detail