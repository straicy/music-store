"""
Запуск: python seed_data.py
Заповнює БД оголошеннями + завантажує фото в Cloudinary.
"""
import asyncio, random, os, urllib.request, json, tempfile
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv
from bson import ObjectId
import cloudinary
import cloudinary.uploader

load_dotenv()
MONGODB_URL   = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "music_store")
pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cloudinary config
cloudinary.config(
    cloud_name="dvasckxfs",
    api_key="798736117412226",
    api_secret="xf21ieJiRrwBTOphS5RUrT02euo",
    secure=True
)

# Picsum IDs для фото
PICSUM_IDS = [145,167,172,180,188,193,209,219,225,230,237,250,257,263,270,274,
              280,287,292,299,305,312,317,326,331,338,343,349,356,362,368,374,
              380,387,393,400,407,145,167,172]

SELLERS = [
    {"name": "Олексій Мельник",  "email": "oleksii@music.ua",  "city": "Київ"},
    {"name": "Дарина Коваль",    "email": "daryna@music.ua",   "city": "Харків"},
    {"name": "Ігор Петренко",    "email": "ihor@music.ua",     "city": "Львів"},
    {"name": "Марія Бондаренко", "email": "mariia@music.ua",   "city": "Одеса"},
    {"name": "Тарас Шевченко",   "email": "taras@music.ua",    "city": "Дніпро"},
    {"name": "Вікторія Лисенко", "email": "viktoria@music.ua", "city": "Запоріжжя"},
    {"name": "Андрій Гриценко",  "email": "andrii@music.ua",   "city": "Полтава"},
]

LISTINGS = [
    {"title":"Fender American Professional II Stratocaster","description":"Легендарна американська стратокастер в ідеальному стані. Купив 2 роки тому, зіграно не більше 50 годин. Комплект: кейс, ремінь, кабель. Звук неперевершений — чистий дзвінкий тон, відмінна сустейн.","price":85000,"category":"guitars","condition":"like_new","brand":"Fender","views":342},
    {"title":"Gibson Les Paul Standard 60s Iced Tea","description":"Gibson Les Paul Standard 60s — один з найкращих інструментів для рок та блюзу. Колір Iced Tea Burst, корпус махагон з кленовим топом. Два хамбакери Burstbucker Pro.","price":112000,"category":"guitars","condition":"good","brand":"Gibson","views":521},
    {"title":"PRS SE Custom 24 Charcoal Burst","description":"PRS SE Custom 24 — корейська серія від легендарного бренду. Відмінний вибір для рокерів і металістів. Граю рідко, стан як новий. Є рідна сумка.","price":28000,"category":"guitars","condition":"like_new","brand":"PRS","views":198},
    {"title":"Gibson SG Standard Heritage Cherry","description":"Класичний Gibson SG Standard — улюблена гітара Тоні Айомі та Ангуса Янга. Колір Heritage Cherry, два хамбакери 490R/490T.","price":78000,"category":"guitars","condition":"good","brand":"Gibson","views":287},
    {"title":"Ibanez RG550 Genesis Purple Neon","description":"Ibanez RG550 — японська гітара для шредерів. Тонка шийка Wizard II та флойд-роза. Колір Purple Neon, стан відмінний.","price":34000,"category":"guitars","condition":"good","brand":"Ibanez","views":445},
    {"title":"Epiphone Les Paul Custom Ebony","description":"Epiphone Les Paul Custom в чорному кольорі. Апгрейд: пікапи Gibson 490R/498T, тюнери Grover. Звучить майже як рідний Gibson.","price":14500,"category":"guitars","condition":"good","brand":"Epiphone","views":312},
    {"title":"Fender Player Telecaster Butterscotch","description":"Fender Player Telecaster мексиканського виробництва. Колір Butterscotch Blonde. Ідеальна для блюзу, кантрі, рок-н-ролу.","price":22000,"category":"guitars","condition":"like_new","brand":"Fender","views":178},
    {"title":"Yamaha Pacifica 612 Translucent Black","description":"Yamaha Pacifica 612 — HSS конфігурація з флоатуючим тремоло. Пікапи Seymour Duncan. Відмінна якість збірки.","price":26000,"category":"guitars","condition":"new","brand":"Yamaha","views":134},
    {"title":"Fender American Performer Precision Bass","description":"Американська P-Bass з пікапом Yosemite Split-Coil. Масивний фундаментальний бас-звук. Колір 3-Color Sunburst.","price":68000,"category":"bass","condition":"like_new","brand":"Fender","views":203},
    {"title":"Music Man StingRay Special 4","description":"Легендарний Music Man StingRay. Активна електроніка 3-Band EQ. Є рідний чохол і документи.","price":95000,"category":"bass","condition":"good","brand":"Music Man","views":387},
    {"title":"Ibanez SR500E Brown Mahogany","description":"Ibanez SR500 — тонка і легка бас-гітара з активними пікапами Bartolini. Ідеальна для фанку та джазу.","price":19500,"category":"bass","condition":"good","brand":"Ibanez","views":156},
    {"title":"Roland RD-2000 Stage Piano 88 клавіш","description":"Roland RD-2000 — флагманський сценічний рояль. 88 молоточкових зважених клавіш PHA-50, движки SuperNATURAL та ZEN-Core.","price":78000,"category":"keyboards","condition":"like_new","brand":"Roland","views":612},
    {"title":"Korg Minilogue XD Analog Synthesizer","description":"Korg Minilogue XD — аналоговий синтезатор. 37 міні-клавіш, 4-голосна поліфонія. Ідеальний для електроніки та ембієнту.","price":24000,"category":"keyboards","condition":"like_new","brand":"Korg","views":445},
    {"title":"Yamaha P-125 Digital Piano","description":"Yamaha P-125 — компактне цифрове піаніно з молоточковою механікою GHS. 88 клавіш, 24 звуки. З підставкою та педальним блоком.","price":18500,"category":"keyboards","condition":"good","brand":"Yamaha","views":298},
    {"title":"Nord Stage 3 Compact 73","description":"Nord Stage 3 — найпрестижніший сценічний інструмент. 73 клавіші, три секції: Piano, Organ, Synth. Понад 500 звуків.","price":145000,"category":"keyboards","condition":"good","brand":"Nord","views":734},
    {"title":"Arturia MiniLab MkII MIDI Controller","description":"Arturia MiniLab MkII — компактний MIDI-контролер з 25 клавішами і 16 пад-кнопками. USB підключення.","price":4200,"category":"keyboards","condition":"like_new","brand":"Arturia","views":187},
    {"title":"Pearl Export EXX 5-Piece Drum Kit","description":"Pearl Export EXX — класичний акустичний набір. 5 барабанів: 22\" BD, 10\"/12\" Tom, 16\" Floor Tom, 14\" Snare. Є тарілки Zildjian.","price":32000,"category":"drums","condition":"good","brand":"Pearl","views":423},
    {"title":"Roland TD-17KVX Electronic Drum Kit","description":"Roland TD-17KVX — електронна ударна установка. Mesh-пади, тихе відтворення. Bluetooth MIDI, понад 310 інструментів.","price":58000,"category":"drums","condition":"like_new","brand":"Roland","views":567},
    {"title":"Zildjian A Custom 4-Piece Cymbal Pack","description":"Комплект тарілок Zildjian A Custom: хай-хет 14\", крешер 16\", крешер 18\", райд 20\". Яскравий звук.","price":28500,"category":"drums","condition":"good","brand":"Zildjian","views":312},
    {"title":"Yamaha YAS-280 Alto Saxophone","description":"Yamaha YAS-280 — альт-саксофон студентського рівня. Позолочений лак, є мундштук, трость і кейс.","price":22000,"category":"wind","condition":"good","brand":"Yamaha","views":234},
    {"title":"Bach Stradivarius 180S37 Bb Trumpet","description":"Bach Stradivarius — найпрестижніша труба у світі. Срібне покриття. Використовувалась у джазовому оркестрі 5 років.","price":48000,"category":"wind","condition":"fair","brand":"Bach","views":178},
    {"title":"Pioneer DJ DDJ-FLX6 4-Channel Controller","description":"Pioneer DDJ-FLX6 — 4-канальний DJ-контролер для rekordbox та Serato. Великі jog wheel, вбудований звуковий інтерфейс.","price":38000,"category":"dj","condition":"like_new","brand":"Pioneer DJ","views":489},
    {"title":"Native Instruments Traktor Kontrol S4 MK3","description":"Traktor Kontrol S4 MK3 — флагманський контролер. 4 канали, аудіоінтерфейс 24bit/96kHz. Traktor Pro 3 у комплекті.","price":42000,"category":"dj","condition":"good","brand":"Native Instruments","views":334},
    {"title":"Shure SM7B Dynamic Microphone","description":"Shure SM7B — легендарний студійний мікрофон. На ньому записані альбоми Майкла Джексона та Metallica. XLR підключення.","price":16500,"category":"studio","condition":"like_new","brand":"Shure","views":678},
    {"title":"Focusrite Scarlett 2i2 (4th Gen)","description":"Focusrite Scarlett 2i2 — найпопулярніший аудіоінтерфейс. 2 входи/2 виходи, 24bit/192kHz. Pro Tools та Ableton у комплекті.","price":7200,"category":"studio","condition":"like_new","brand":"Focusrite","views":423},
    {"title":"Audio-Technica ATH-M50x Headphones","description":"Audio-Technica ATH-M50x — стандарт студійного моніторингу. Закрита конструкція, 45мм драйвери. Три кабелі в комплекті.","price":5800,"category":"studio","condition":"good","brand":"Audio-Technica","views":312},
    {"title":"Yamaha HS8 Studio Monitor (пара)","description":"Пара студійних моніторів Yamaha HS8. Точна нейтральна АЧХ. 8-дюймові вуфери, 75W+45W. Мало використовувались.","price":32000,"category":"studio","condition":"like_new","brand":"Yamaha","views":445},
    {"title":"D'Addario EXL110 Strings (10 комплектів)","description":"D'Addario EXL110 — найпопулярніші струни. Regular Light 10-46. 10 комплектів у вакуумній упаковці.","price":850,"category":"accessories","condition":"new","brand":"D'Addario","views":567},
    {"title":"Boss TU-3 Chromatic Tuner Pedal","description":"Boss TU-3 — стандарт педальних тюнерів. Точність ±1 цент. True bypass або буферний режим.","price":3200,"category":"accessories","condition":"good","brand":"Boss","views":234},
    {"title":"Ibanez Tube Screamer TS9 Overdrive","description":"Ibanez TS9 Tube Screamer — легендарна педаль овердрайву Stevie Ray Vaughan та John Mayer.","price":4800,"category":"accessories","condition":"like_new","brand":"Ibanez","views":389},
    {"title":"Electro-Harmonix Big Muff Pi Fuzz","description":"EHX Big Muff Pi — символ гранжу. Девід Гілмор та Kurt Cobain використовували саме її.","price":3600,"category":"accessories","condition":"good","brand":"Electro-Harmonix","views":312},
    {"title":"Jim Dunlop Cry Baby GCB95 Wah","description":"Jim Dunlop Cry Baby — найвідоміша Wah педаль у світі. Міцний металевий корпус.","price":4200,"category":"accessories","condition":"like_new","brand":"Jim Dunlop","views":267},
    {"title":"Shure GLXD16 Guitar Wireless System","description":"Shure GLXD16 — бездротова система для гітари. До 16 годин заряду. Для живих виступів.","price":14500,"category":"accessories","condition":"like_new","brand":"Shure","views":223},
    {"title":"Fender Deluxe Molded Guitar Case","description":"Оригінальний кейс Fender Deluxe для Stratocaster/Telecaster. Жорсткий корпус, м'яке оздоблення.","price":3800,"category":"accessories","condition":"good","brand":"Fender","views":145},
    {"title":"Roland PM-03 Personal Monitor 20W","description":"Roland PM-03 — персональний монітор для електронних барабанів і клавішних. 5-дюймовий вуфер, 20W.","price":8500,"category":"accessories","condition":"like_new","brand":"Roland","views":134},
    {"title":"Ernie Ball Regular Slinky (12 комплектів)","description":"Ernie Ball Regular Slinky — улюблені Slash та Eric Clapton. 12 комплектів 10-46 у запаяних пакетах.","price":980,"category":"accessories","condition":"new","brand":"Ernie Ball","views":423},
    {"title":"Yamaha Silent Violin SV-200","description":"Yamaha SV-200 — електроакустична скрипка для беззвучних репетицій. 4-канальний передпідсилювач.","price":24000,"category":"strings","condition":"good","brand":"Yamaha","views":198},
]


def upload_to_cloudinary(picsum_id, listing_id):
    try:
        url = f"https://picsum.photos/id/{picsum_id}/800/600.jpg"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            img_data = resp.read()

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(img_data)
            tmp_path = tmp.name

        result = cloudinary.uploader.upload(
            tmp_path,
            folder=f"music_store/{listing_id}",
            resource_type="image",
            transformation=[{"width": 800, "height": 600, "crop": "fill", "quality": "auto"}]
        )
        os.unlink(tmp_path)
        return result["secure_url"]
    except Exception as e:
        print(f"      ⚠️  {e}")
        return None


async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("🌱 Починаємо заповнення БД...\n")
    await db.listings.delete_many({"is_seed": True})
    await db.users.delete_many({"is_seed": True})
    print("🗑️  Старі seed-дані видалено\n")

    seller_ids = []
    for s in SELLERS:
        existing = await db.users.find_one({"email": s["email"]})
        if existing:
            seller_ids.append({"id": str(existing["_id"]), "name": s["name"], "city": s["city"]})
            continue
        result = await db.users.insert_one({
            "name": s["name"], "email": s["email"],
            "password_hash": pwd_context.hash("password123"),
            "phone": None, "bio": None, "city": s["city"],
            "avatar": None, "role": "user", "is_banned": False,
            "listings_count": 0, "is_seed": True,
            "created_at": datetime.now() - timedelta(days=random.randint(30, 365)),
            "updated_at": datetime.now(),
        })
        seller_ids.append({"id": str(result.inserted_id), "name": s["name"], "city": s["city"]})
        print(f"  👤 {s['name']}")

    print(f"\n📸 Створюємо {len(LISTINGS)} оголошень з фото в Cloudinary...\n")

    for i, l in enumerate(LISTINGS):
        seller  = random.choice(seller_ids)
        created = datetime.now() - timedelta(days=random.randint(1, 90))

        result = await db.listings.insert_one({
            "title": l["title"], "description": l["description"],
            "price": l["price"], "category": l["category"],
            "condition": l["condition"], "brand": l.get("brand"),
            "city": seller["city"], "attributes": {},
            "images": [], "status": "active",
            "seller_id": seller["id"], "seller_name": seller["name"],
            "seller_avatar": None, "views": l.get("views", 50),
            "is_seed": True, "created_at": created, "updated_at": created,
        })
        lid = str(result.inserted_id)

        picsum_id = PICSUM_IDS[i % len(PICSUM_IDS)]
        print(f"  [{i+1}/{len(LISTINGS)}] {l['title'][:48]}...")

        img_url = upload_to_cloudinary(picsum_id, lid)
        if img_url:
            await db.listings.update_one(
                {"_id": result.inserted_id},
                {"$set": {"images": [img_url]}}
            )
            print(f"      ✅ {img_url[:50]}...")

        await db.users.update_one(
            {"_id": ObjectId(seller["id"])},
            {"$inc": {"listings_count": 1}}
        )

    print(f"\n🎉 Готово! {len(LISTINGS)} оголошень додано з фото в Cloudinary!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
