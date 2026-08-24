
# 2.1 Data inspection:

### What information about a product do we care about?


- Product Metadata
  - prduct_id
  - title_fa
  - title_en
  - url
```json
"product": {
    "id": 20188437,
    "title_fa": "شلوار جین راسته مردانه دیان مدل TR-RA",
    "title_en": "",
    "url": {
        "base": null,
        "uri": "/product/dkp-20188437/شلوار-جین-راسته-مردانه-دیان-مدل-tr-ra"
}
```
---
- Product brand.
```json
"brand": {
    "code": "diyan",
    "title_fa": "دیان",
    "title_en": "Diyan",
    "url": {
        "base": null,
        "uri": "/brand/diyan/"
    },
    "logo": {
        "url": [
            "https://dkstatics-public.digikala.com/digikala-brands/100012106.jpg?x-oss-process=image/resize,m_lfit,h_120,w_120/quality,q_80"
        ],
},
```
---
-  Category associated to the product
-  item_categories [item_category2, 3, 4, 5] (Helpful for context)

```json
"data_layer": {
                "brand": "دیان",
                "category": "[AP,جین مردانه]",
                "item_category2": "مد و پوشاک",
                "item_category3": "مردانه",
                "item_category4": "لباس مردانه",
                "item_category5": "شلوار جین مردانه"
            },
```

---
I don't know what are these but they could be helpful:
- test_title_fa
- test_title_en

```json
 "product_type": "product",
            "test_title_fa": "شلوار جین راسته مردانه دیان مدل TR-RA با پارچه جین نیم کش، فاق متوسط با بسته شدن دکمه و زیپ، چهار جیب، تنخور معمولی و مناسب استفاده در تمام فصول",
            "test_title_en": "",
```
---

- Product images for image retrieval phase.


```json
"markup_schema": [
    {
        "name": "شلوار جین راسته مردانه دیان مدل TR-RA",
        "image": [
            "https://dkstatics-public.digikala.com/digikala-products/0084a38381770a81842d6d6edc913d81de513204_1756026380.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/baa233258e7d94aed8c2b9be37e78f4ec8877521_1756026390.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/3bb515e8b0a689747d1349ab7a2b825539dff8c3_1755449934.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/70903b30a47c62b8222afeb5a41455f5e384373e_1755449922.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/6d2d6a11b58eac67a8c2f4a32c0cbf965855a415_1755449937.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/853f41b7f0b2714190a0056b16efdc22085c8aad_1755449941.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/0e89825e93c74c01a3bdf41cd8bb1eccd763a15d_1755449925.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/a430961e52a56b41287ae5d1a344d673932c504f_1755449919.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/a5a2e8ecad807d3b580e3cab2b9be982a0dc18e6_1755449928.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/baa233258e7d94aed8c2b9be37e78f4ec8877521_1756026395.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/6ab23c85c7402e4b7e50b6f7a55150f80d823a35_1767731018.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/6e7c53d5b4b3909f746425bcce238f63609dd28f_1767731023.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/c0d5d2a5a0d0513495085dcc59dfa6309b45d144_1767731028.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/5c70e00630fef0effac2fcef0c78612207e98103_1767731033.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/a80a49106bd75fc1ed1fe39d354d726a1d98b19f_1767731040.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/3735af848678a5767f6757d7751ff6bc93bf4146_1767731053.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/9b0f5e6759f36278ffa0468447256aeb0373f866_1767731063.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/6f20d015909323f50b6f068e861761fb1a7093e4_1767731068.jpg?x-oss-process=image/resize,h_1600/quality,q_80",
            "https://dkstatics-public.digikala.com/digikala-products/edd556a42ed0cc18d986e570394678ca8895261f_1777231793.jpg?x-oss-process=image/resize,h_1600/quality,q_80"
        ],
        "description": "خرید اینترنتی شلوار جین راسته مردانه دیان مدل TR-RA با رنگبندی آبی تیره، مشکی، ذغالی به همراه مقایسه، بررسی مشخصات و لیست قیمت امروز در فروشگاه اینترنتی دیجی‌کالا",
```
---
- Product ratings.
```json
"rating": {
    "rate": 85.09,
    "count": 106
```
---
    
- Product colors.
```json
"colors": [
    {
        "title": "آبی تیره",
        "hex_code": "#020266",
    },
    {
        "title": "مشکی",
        "hex_code": "#000000",
    },
    {
        "title": "ذغالی",
        "hex_code": "#333333",
        "images": []
    }
],
```
---
- Product price.

```json
"price": {
        "selling_price": 17300000,    
},
```
---

- Product variants (size , price, ...).
  
```json
"variants": [
        "size": {
            "id": 42100103,
            "title": "آبی تیره - 50"
        }
    ]
```
---
- Product review
  - description
  - attributes

```json
"review": {
    "description": "شلوار جین همواره یکی از پوشش های مورد توجه آقایان و بانوان در چندین دهه ی گذشته بوده و هست . با توجه به استقبال خوب مشتریان عزیز . این شلوار دارای دو جیب در جلو و دو جیب در پشت میباشد. پارچه ی استفاده شده در این محصول نیم کش میباشد و فاق آن با زیپ بسته میشود. برای انتخاب سایز مناسب میتوانید به جدول سایزی که در قسمت تصاویر بارگذاری شده است مراجعه نمایید.در ضمن این محصول در سایزبندی ایرانی تولید و عرضه شده است.",
    "attributes": [
        {
            "title": "تنخور لباس",
            "values": [
                "معمولی (regular fit)"
            ]
        },
        {
            "title": "قد لباس",
            "values": [
                "تا مچ پا"
            ]
        },
        {
            "title": "مناسب برای فصل",
            "values": [
                "زمستان",
                "پاییز",
                "تابستان",
                "بهار"
            ]
        },
        {
            "title": "جنس",
            "values": [
                "پلی استر",
                "جین"
            ]
        },
        {
            "title": "استایل لباس",
            "values": [
                "راسته"
            ]
        },
        {
            "title": "نوع فاق",
            "values": [
                "متوسط"
            ]
        },
        {
            "title": "نحوه بسته شدن",
            "values": [
                "دکمه و زیپ"
            ]
        }
    ]
},
"pros_and_cons": {
    "advantages": [],
    "disadvantages": []
},
```
---
- Product Specifications.

```json
"specifications": [
            {
                "title": "مشخصات",
                "attributes": [
                    {
                        "title": "تنخور لباس",
                        "values": [
                            "معمولی (regular fit) "
                        ]
                    },
                    {
                        "title": "قد لباس",
                        "values": [
                            "تا مچ پا "
                        ]
                    },
                    {
                        "title": "مناسب برای فصل",
                        "values": [
                            "زمستان ",
                            "پاییز ",
                            "تابستان ",
                            "بهار "
                        ]
                    },
                    {
                        "title": "جنس",
                        "values": [
                            "پلی استر ",
                            "جین "
                        ]
                    },
                    {
                        "title": "استایل لباس",
                        "values": [
                            "راسته "
                        ]
                    },
                    {
                        "title": "نوع فاق",
                        "values": [
                            "متوسط "
                        ]
                    },
                    {
                        "title": "نحوه بسته شدن",
                        "values": [
                            "دکمه و زیپ "
                        ]
                    },
                    {
                        "title": "توضیحات جنس",
                        "values": [
                            "جین نیم کش "
                        ]
                    },
                    {
                        "title": "جزئیات",
                        "values": [
                            "(پارچه جین نیم کش)  (تن خوری راسته )  (دارای چهار جیب)  (رنگ آبی تیره)  (سنگشور رادو محو)  (برند دیان)  (بسته شدن فاق با زیپ)  (سایزبندی ایرانی)  (جدول انتخاب سایز در قسمت تصاویر) "
                        ]
                    },
                    {
                        "title": "نگهداری",
                        "values": [
                            "در هنگام شست و شو ، شلوار را پشت و رو کرده و حدالامکان از جین شور و آب سرد استفاده نمایید. "
                        ]
                    }
                ]
            }
        ],
```
---

- SEO title & description (Helpful for the context).
```json
"seo": {
    "title": "قیمت و خرید شلوار جین راسته مردانه دیان مدل TR-RA",
    "description": "خرید اینترنتی شلوار جین راسته مردانه دیان مدل TR-RA با رنگبندی آبی تیره، مشکی، ذغالی به همراه مقایسه، بررسی مشخصات و لیست قیمت امروز در فروشگاه اینترنتی دیجی‌کالا",
```
---
- Comments overview (Generated by Digikala for each product).
  
```json
"comments_overview": {
    "id": 403406,
    "overview": "بسیاری از کاربران از جنس و دوخت شلوار جین دیان رضایت کامل دارند و معتقدند که کیفیت پارچه و دوخت در مجموع خوب است. همچنین سایزبندی دقیق و مطابق با انتظار آنها بوده و برای استفاده روزمره مناسب است. رنگ و تن خور محصول نیز مورد تحسین قرار گرفته است و محصول را در کلیت کیفیت خوبی دانسته‌اند.\nبرخی کاربران از نازک بودن پارچه و احتمال کیفیت پایین تر نسبت به قبل گلایه دارند و معتقدند که جنس ممکن است به زودی پس داده یا پرز بدهد. همچنین نظراتی در مورد سایزهای متفاوت، ناتوانی در ست کردن لباس با مراسم‌های خاص و نارضایتی از کاهش کیفیت پارچه نسبت به دفعات قبل وجود دارد. برخی کاربران جنس را معمولی و چندان باکیفیت نمی‌دانند و از ناپایداری رنگ پس از شستشو شکایت کرده‌اند.\nدر مجموع، محصولی با کیفیت مناسب و قیمت قابل قبول است که برای استفاده روزمره گزینه‌ای خوبی محسوب می‌شود، هرچند در ساخت و جنس پارچه مسائل کوچکی قابل مشاهده است. کاربران کلی از خرید خود راضی هستند و توصیه می‌کنند، اما پیشنهاد داده‌اند سایزها را یک شماره بزرگ‌تر بگیرند تا به راحتی و مطابق انتظار باشد.",
    "advantages": [
        "کیفیت مناسب پارچه و دوخت",
        "سایزبندی دقیق",
        "رنگ و تن خور خوب"
    ],
    "disadvantages": [
        "پُرز دادن پارچه",
        "پارچه نازک و حساس"
    ]
},
```
---
- Product Q&A, top 5 (for now).
  
```json
{
    "text": "دوستانی که خرید کردید اندازه ها استاندارد بود؟\n با وزن ۸۷ کیلو ۴۶ مناسبه یا ۴۴؟\nممنون میشم پاسخ بدین",
    "answer_count": 4,
        {
            "text": "۴۴ بدون کمر بند اگه اندازه دور شکم کوچک باشد",
            "reactions": {
                "likes": 0,
                "dislikes": 3
            },
        },
        {
            "text": "44 کمی تنگ و 46 کمی گشاد",
            "reactions": {
                "likes": 0,
                "dislikes": 0
            },
        },
        {
            "text": "سلام جنسش خوبه رنگش عالی ولی هر سایزی هستی به سایز بیشتر بگیر",
            "reactions": {
                "likes": 0,
                "dislikes": 0
            },
        },
        {
            "text": "من با وزن ۷۴ شماره ۵۲گرفتم",
            "reactions": {
                "likes": 0,
                "dislikes": 1
            },
        }
    ]
}
```