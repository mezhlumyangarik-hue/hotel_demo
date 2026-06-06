from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_for_hotel"

# JSON ֆայլի անունը, որտեղ կպահվեն տվյալները, որպեսզի երբեք չկորչեն
BOOKINGS_FILE = "bookings.json"

# Ֆունկցիա՝ բազայից տվյալները կարդալու համար
def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        # Եթե ֆայլը չկա, ստեղծում ենք սկզբնական դեմո տվյալով
        initial_data = [{
            "name": "Արմեն Հակոբյան", 
            "room": "Deluxe Սենյակ", 
            "checkin": "2026-06-10", 
            "checkout": "2026-06-15", 
            "nights": 5, 
            "total": "$600"
        }]
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Ֆունկցիա՝ նոր պատվերը ֆայլի մեջ ավելացնելու համար
def save_booking(new_booking):
    current_bookings = load_bookings()
    current_bookings.append(new_booking)
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_bookings, f, ensure_ascii=False, indent=4)

rooms = [
    {
        "id": 1, 
        "name": "Deluxe Սենյակ", 
        "price": "$120 / գիշեր", 
        "features": "2 անձ | Անվճար Wi-Fi | Պատշգամբ", 
        "image": "images/room1.jpg"  # Փոխվեց տեղական հասցեի
    },
    {
        "id": 2, 
        "name": "Լյուքս Համար", 
        "price": "$250 / գիշեր", 
        "features": "4 անձ | Ջակուզի | Նախաճաշ ներառված", 
        "image": "images/room2.jpg"  # Փոխվեց տեղական հասցեի
    },
    {
        "id": 3, 
        "name": "Նախագահական Սուիթ", 
        "price": "$500 / գիշեր", 
        "features": "Անհատական լողավազան | Մինի բար | Panoramic տեսարան", 
        "image": "images/room3.jpg"  # Փոխվեց տեղական հասցեի
    }
]

@app.route('/')
def home():
    amenities = [
        {"icon": "🏊‍♂️", "title": "Լողավազան"},
        {"icon": "🏋️‍♂️", "title": "Ֆիտնես Կենտրոն"},
        {"icon": "🍳", "title": "Ռեստորան"},
        {"icon": "🚗", "title": "Կայանատեղի"}
    ]
    return render_template('index.html', rooms=rooms, amenities=amenities)

@app.route('/book', methods=['POST'])
def book():
    if request.method == 'POST':
        name = request.form.get('name')
        room_name = request.form.get('room')
        checkin_str = request.form.get('checkin')
        checkout_str = request.form.get('checkout')
        
        room_price = 120
        for r in rooms:
            if r['name'] == room_name:
                room_price = int(r['price'].split()[0].replace('$', ''))

        try:
            d1 = datetime.strptime(checkin_str, "%Y-%m-%d")
            d2 = datetime.strptime(checkout_str, "%Y-%m-%d")
            nights = (d2 - d1).days
        except ValueError:
            flash("Ամսաթվերի սխալ ֆորմատ:")
            return redirect(url_for('home') + '#booking')
        
        if nights <= 0:
            flash("Սխալ ամսաթվեր: Մեկնման օրը պետք է լինի ժամանման օրվանից ուշ:")
            return redirect(url_for('home') + '#booking')

        total_price = nights * room_price

        # Ստեղծում ենք նոր ամրագրման օբյեկտը
        new_booking = {
            "name": name,
            "room": room_name,
            "checkin": checkin_str,
            "checkout": checkout_str,
            "nights": nights,
            "total": f"${total_price}"
        }
        
        # Պահում ենք JSON ֆայլի մեջ (էլ երբեք չի կորչի)
        save_booking(new_booking)
        
        flash(f"Շնորհակալությո՛ւն: Ամրագրվեց {nights} գիշեր: Ընդհանուր գումարը՝ ${total_price}:")
        return redirect(url_for('home') + '#booking')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    ADMIN_PASSWORD = "admin1234"
    
    # Տվյալները կարդում ենք ֆայլից
    current_bookings = load_bookings()
    
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == ADMIN_PASSWORD:
            return render_template('admin.html', bookings=current_bookings, authenticated=True)
        else:
            flash("Սխալ գաղտնաբառ: Մուտքն արգելված է:", "admin_error")
            return render_template('admin.html', authenticated=False)
            
    return render_template('admin.html', authenticated=False)

@app.route('/delete-booking/<int:booking_index>', methods=['POST'])
def delete_booking(booking_index):
    # Կարդում ենք ընթացիկ ամրագրումները JSON-ից
    current_bookings = load_bookings()
    
    # Ստուգում ենք՝ արդյոք այդ ինդեքսով պատվեր գոյություն ունի
    if 0 <= booking_index < len(current_bookings):
        # Ջնջում ենք այդ պատվերը ցուցակից
        current_bookings.pop(booking_index)
        
        # Թարմացված ցուցակը նորից գրում ենք JSON ֆայլի մեջ
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current_bookings, f, ensure_ascii=False, indent=4)
            
    # Ջնջելուց հետո ադմինին ետ ենք ուղարկում նույն ադմին էջը
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Կարևոր է Render-ի համար. վերցնում է պորտը միջավայրից, եթե չկա՝ դնում է 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)