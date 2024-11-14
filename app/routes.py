from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import License
from app import db
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    licenses = License.query.all()
    return render_template('index.html', licenses=licenses)

@main.route('/add', methods=['POST'])
def add_license():
    key = request.form['key']
    days = int(request.form['days'])
    hours = int(request.form['hours'])
    subscription_type = request.form['subscription_type']
    support_name = request.form['support_name']
    key_type = request.form['key_type']

    expiration_date = datetime.now() + timedelta(days=days, hours=hours)

    if subscription_type == "1 Week":
        expiration_date += timedelta(weeks=1)
    elif subscription_type == "1 Month":
        expiration_date += timedelta(weeks=4)
    elif subscription_type == "3 Months":
        expiration_date += timedelta(weeks=12)
    elif subscription_type == "6 Months":
        expiration_date += timedelta(weeks=24)
    elif subscription_type == "1 Year":
        expiration_date += timedelta(weeks=52)

    new_license = License(
        key=key,
        expiration_date=expiration_date,
        subscription_type=subscription_type,
        support_name=support_name,
        key_type=key_type
    )

    db.session.add(new_license)
    db.session.commit()

    return redirect(url_for('main.index'))

@main.route('/list_licenses', methods=['GET'])
def list_licenses():
    licenses = License.query.all()
    return jsonify([license.to_dict() for license in licenses])

@main.route('/reset_key', methods=['POST'])
def reset_key():
    key = request.form['key']
    license = License.query.filter_by(key=key).first()
    if license:
        license.device_id = None
        license.activated = False
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/toggle_active/<int:id>')
def toggle_active(id):
    license = License.query.get(id)
    if license:
        license.active = not license.active
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete/<int:id>')
def delete_license(id):
    license = License.query.get(id)
    if license:
        db.session.delete(license)
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/check_key_details', methods=['POST'])
def check_key_details():
    data = request.json
    key = data.get('key')
    device_id = data.get('device_id')

    license = License.query.filter_by(key=key).first()
    if not license:
        return jsonify({'valid': False, 'reason': 'Key not found.'})

    if license.activated and license.device_id != device_id:
        return jsonify({'valid': False, 'reason': 'This key is already used on another device.'})

    if not license.activated:
        license.device_id = device_id
        license.activated = True
        db.session.commit()

    if license.active and license.expiration_date > datetime.now():
        remaining_time = license.expiration_date - datetime.now()
        remaining_minutes = (remaining_time.days * 24 * 60) + (remaining_time.seconds // 60)

        return jsonify({
            'valid': True,
            'expiration_date': license.expiration_date.strftime('%Y-%m-%d'),
            'subscription_type': license.subscription_type,
            'support_name': license.support_name,
            'remaining_time': {
                'days': remaining_time.days,
                'hours': remaining_time.seconds // 3600,
                'minutes': remaining_minutes % 60
            }
        })

    return jsonify({'valid': False, 'reason': 'The key is either inactive or expired.'})