from django.core.management.base import BaseCommand
from dashboard.models import Sklad


class Command(BaseCommand):
    help = 'Populate Sklad with test data'

    def handle(self, *args, **options):
        # Test data as provided by the user
        test_data = [
            {
                'article_number': '0003001001',
                'name': 'Tota Quartz 9000 5w40 1L',
                'unit': 'бр',
                'quantity': 16.00,
                'purchase_price': 8.80,
                'is_active': True
            },
            {
                'article_number': '0003001002',
                'name': 'Total Quartz 9000 5W40 4L',
                'unit': 'бр',
                'quantity': 6.00,
                'purchase_price': 30.96,
                'is_active': True
            },
            {
                'article_number': '0003001003',
                'name': 'Total Quartz 9000 5W40 5L',
                'unit': 'бр',
                'quantity': 13.00,
                'purchase_price': 39.32,
                'is_active': True
            },
            {
                'article_number': '000300100301',
                'name': 'Total Quartz 7000 10W40 5L',
                'unit': 'л',
                'quantity': 3.00,
                'purchase_price': 49.56,
                'is_active': True
            },
            {
                'article_number': '00030010030102',
                'name': 'Total Quatrz 7000 10W40 4L',
                'unit': 'л',
                'quantity': 5.00,
                'purchase_price': 24.92,
                'is_active': True
            },
            {
                'article_number': '000300100303',
                'name': 'Total 7000 Energy 10W40 1л.',
                'unit': 'л',
                'quantity': 2.00,
                'purchase_price': 7.68,
                'is_active': True
            },
            {
                'article_number': '00030010030301',
                'name': 'Total 7000 Energy 10W40 4л.',
                'unit': 'л',
                'quantity': 1.00,
                'purchase_price': 27.92,
                'is_active': True
            },
            # Additional test data
            {
                'article_number': '00030010040105',
                'name': 'Total INEO RCP 5W30 масло 1л.',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 15.76,
                'is_active': True
            },
            {
                'article_number': '00030010040106',
                'name': 'Total INEO RCP 5W30 масло 5л.',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 73.61,
                'is_active': True
            },
            {
                'article_number': '00030020010001',
                'name': 'Total trans gear 8 75W80 1L',
                'unit': 'бр',
                'quantity': 19.00,
                'purchase_price': 9.82,
                'is_active': True
            },
            {
                'article_number': '000300200100041',
                'name': 'Total fluid matic MV 1л',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 12.31,
                'is_active': True
            },
            {
                'article_number': '0003002001001',
                'name': 'Total LHM Plus 1L',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 7.74,
                'is_active': True
            },
            {
                'article_number': '0003002001002',
                'name': 'Total fluide ATX 1L',
                'unit': 'бр',
                'quantity': 5.00,
                'purchase_price': 12.87,
                'is_active': True
            },
            {
                'article_number': '000300200100201',
                'name': 'total Fluide LDS 1L',
                'unit': 'бр',
                'quantity': 9.00,
                'purchase_price': 12.56,
                'is_active': True
            },
            {
                'article_number': '000300200100301',
                'name': 'Total Glacelf classic 1L',
                'unit': 'бр',
                'quantity': 12.00,
                'purchase_price': 6.67,
                'is_active': True
            },
            {
                'article_number': '000300800101',
                'name': 'INJECTION 10W40 1L полусинт.двиг.масло',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 6.41,
                'is_active': True
            },
            {
                'article_number': '00030090010101',
                'name': 'Magnatac 5W40 C3 4л синт.двиг.масло',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 59.84,
                'is_active': True
            },
            {
                'article_number': '000300900103',
                'name': 'Magnatec SS 5W30 A5 1л синт.двиг.масло Stop-Start',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 15.60,
                'is_active': True
            },
            {
                'article_number': '0003009003',
                'name': 'Multitech 10W40 1L',
                'unit': 'бр',
                'quantity': 8.00,
                'purchase_price': 7.01,
                'is_active': True
            },
            {
                'article_number': '0009902907',
                'name': 'части по дизелова гпр.с-ма',
                'unit': 'кг',
                'quantity': 5.00,
                'purchase_price': 5.24,
                'is_active': True
            },
            {
                'article_number': '0216-00-5551475P',
                'name': 'картер',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 136.50,
                'is_active': True
            },
            {
                'article_number': '0219-04-0020P',
                'name': 'мека връзза, изп.с-ма',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 15.07,
                'is_active': True
            },
            {
                'article_number': '037660',
                'name': 'болт',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 12.34,
                'is_active': True
            },
            {
                'article_number': '080735',
                'name': 'семеринг',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 30.99,
                'is_active': True
            },
            {
                'article_number': '09-0130GT',
                'name': 'въздуховод за турбина',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 43.46,
                'is_active': True
            },
            {
                'article_number': '0986280408',
                'name': 'импулсен датчик колянов вал',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 28.66,
                'is_active': True
            },
            {
                'article_number': '0986580261',
                'name': 'горивна помпа-бензин',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 160.13,
                'is_active': True
            },
            {
                'article_number': '0986580310',
                'name': 'горивна помпа - бензин',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 138.17,
                'is_active': True
            },
            {
                'article_number': '100150FEBI',
                'name': 'тампон двигател',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 75.95,
                'is_active': True
            },
            {
                'article_number': '102784',
                'name': '8100 X-CESS 5W40 - 1L',
                'unit': 'бр',
                'quantity': 7.00,
                'purchase_price': 14.71,
                'is_active': True
            },
            {
                'article_number': '102870',
                'name': '8100 X-CESS 5W40 - 5L',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 77.30,
                'is_active': True
            },
            {
                'article_number': '104243',
                'name': '300V CHRONO 10W40-2L',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 58.63,
                'is_active': True
            },
            {
                'article_number': '104256',
                'name': '8100 X-CESS 5W40-4L',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 53.96,
                'is_active': True
            },
            {
                'article_number': '107787',
                'name': 'VISION WINTER 20C-5L',
                'unit': 'бр',
                'quantity': 8.00,
                'purchase_price': 10.97,
                'is_active': True
            },
            {
                'article_number': '108534',
                'name': '8100 ECO-LITE 0W20-1L',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 20.61,
                'is_active': True
            },
            {
                'article_number': '108536',
                'name': '8100 ECO-LITE 0W20-5L',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 88.19,
                'is_active': True
            },
            {
                'article_number': '109470',
                'name': '8100 X-CLEAN EFE 5W30 1L',
                'unit': 'бр',
                'quantity': 6.00,
                'purchase_price': 15.95,
                'is_active': True
            },
            {
                'article_number': '10DZ174001307',
                'name': 'двигател Citroen C5/ VF7D4HXB76224139',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 354.16,
                'is_active': True
            },
            {
                'article_number': '1109.AL',
                'name': 'филтър маслен',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 7.81,
                'is_active': True
            },
            {
                'article_number': '11142249534',
                'name': 'семеринг колянов вал преден',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 43.97,
                'is_active': True
            },
            {
                'article_number': '11-160200023',
                'name': 'външен кормилен накрайник',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 30.12,
                'is_active': True
            },
            {
                'article_number': '11-160310025',
                'name': 'кормилна стр.щанга без накрайник',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 25.68,
                'is_active': True
            },
            {
                'article_number': '11667794767',
                'name': 'гарнитури к-кт, вакуум помпа',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 8.25,
                'is_active': True
            },
            {
                'article_number': '13.0460-3876.2',
                'name': 'спирачни накладки',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 103.95,
                'is_active': True
            },
            {
                'article_number': '1308CX',
                'name': 'капаче резистор вентилатор',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 9.30,
                'is_active': True
            },
            {
                'article_number': '13850986013850',
                'name': 'сатртер 12V 0.9KW',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 88.83,
                'is_active': True
            },
            {
                'article_number': '1.42E+11',
                'name': 'уплътнение',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 2.20,
                'is_active': True
            },
            {
                'article_number': '1608501380',
                'name': 'ключалка, преден капак',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 63.84,
                'is_active': True
            },
            {
                'article_number': '1609232380',
                'name': 'акумулатор 70/640 - 278/175/190',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 99.50,
                'is_active': True
            },
            {
                'article_number': '1609232680',
                'name': 'акумулатор L2D 60/540',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 83.94,
                'is_active': True
            },
            {
                'article_number': '1609999080',
                'name': 'филтър поленов ERP',
                'unit': 'бр',
                'quantity': 10.00,
                'purchase_price': 16.87,
                'is_active': True
            },
            {
                'article_number': '1610497280',
                'name': 'капачка филтър климатик',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 22.93,
                'is_active': True
            },
            {
                'article_number': '1611659180',
                'name': 'филтър горивен',
                'unit': 'бр',
                'quantity': 15.00,
                'purchase_price': 17.63,
                'is_active': True
            },
            {
                'article_number': '1611659480',
                'name': 'филтър горивен ERP',
                'unit': 'бр',
                'quantity': 14.00,
                'purchase_price': 28.77,
                'is_active': True
            },
            {
                'article_number': '1613561780',
                'name': 'ангренажен ремък',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 328.95,
                'is_active': True
            },
            {   
                'article_number': '1622750380',
                'name': 'щипка',
                'unit': 'м',
                'quantity': 30.00,
                'purchase_price': 1.06,
                'is_active': True
            },
            {
                'article_number': '1623159380',
                'name': 'втулка гумена',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 2.96,
                'is_active': True
            },
            {
                'article_number': '1623179680',
                'name': 'семеринг десен полувал',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 19.43,
                'is_active': True
            },
            {
                'article_number': '1629085380',
                'name': 'акумулатор 60Ah 640A',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 151.86,
                'is_active': True
            },
            {
                'article_number': '1636051880',
                'name': 'течност за чистачки зимна -30 1л.',
                'unit': 'бр',
                'quantity': 5.00,
                'purchase_price': 2.49,
                'is_active': True
            },
            {
                'article_number': '1636264180',
                'name': 'обезмаслител',
                'unit': 'бр',
                'quantity': 6.00,
                'purchase_price': 3.52,
                'is_active': True
            },
            {
                'article_number': '1637756080',
                'name': 'антифриз 1л. -70*',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 10.13,
                'is_active': True
            },
            {
                'article_number': '1638027780',
                'name': 'филтър въздушен ERP',
                'unit': 'бр',
                'quantity': 13.00,
                'purchase_price': 12.93,
                'is_active': True
            },
            {
                'article_number': '1638155580',
                'name': 'добавък EGR',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 88.01,
                'is_active': True
            },
            {
                'article_number': '164005420R',
                'name': 'филтър горивен',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 84.66,
                'is_active': True
            },
            {
                'article_number': '1643624980',
                'name': 'филтър горивен ERP',
                'unit': 'бр',
                'quantity': 8.00,
                'purchase_price': 23.68,
                'is_active': True
            },
            {
                'article_number': '1671544080',
                'name': 'тампон преден амортисьор',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 31.61,
                'is_active': True
            },
            {
                'article_number': '1680233580',
                'name': 'филтър маслен ERP',
                'unit': 'бр',
                'quantity': 6.00,
                'purchase_price': 8.03,
                'is_active': True
            },
            {
                'article_number': '1682730080',
                'name': 'шарнир ERP',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 87.23,
                'is_active': True
            },
            {
                'article_number': '1682954080',
                'name': 'филтър маслен',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 8.73,
                'is_active': True
            },
            {
                'article_number': '1684449980',
                'name': 'уплътнение дюза',
                'unit': 'бр',
                'quantity': 4.00,
                'purchase_price': 4.96,
                'is_active': True
            },
            {
                'article_number': '1690642080',
                'name': 'филтър горивен',
                'unit': 'бр',
                'quantity': 22.00,
                'purchase_price': 25.48,
                'is_active': True
            },
            {
                'article_number': '1693660680',
                'name': 'акумулатор Стоп/старт 12V 70Ah 760A',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 245.17,
                'is_active': True
            },
            {
                'article_number': '19060C0',
                'name': 'филтър горивен',
                'unit': 'бр',
                'quantity': 2.00,
                'purchase_price': 21.78,
                'is_active': True
            },
            {
                'article_number': '193339',
                'name': 'регулатор',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 212.33,
                'is_active': True
            },
            {
                'article_number': '1986S00744',
                'name': 'стартер 12V 2.0kW',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 166.95,
                'is_active': True
            },
            {
                'article_number': '20371-0010-99',
                'name': 'SYNT RSP 210 SAE 0W-20 1L',
                'unit': 'бр',
                'quantity': 3.00,
                'purchase_price': 16.69,
                'is_active': True
            },
            {
                'article_number': '21010-0015-03',
                'name': 'ANTOFREEZ AN 1.5л.',
                'unit': 'бр',
                'quantity': 11.00,
                'purchase_price': 9.19,
                'is_active': True
            },
            {
                'article_number': '21014-0015-99',
                'name': 'антифриз AN-SF 12+ 1.5л.',
                'unit': 'бр',
                'quantity': 30.00,
                'purchase_price': 9.25,
                'is_active': True
            },
            {
                'article_number': '228.512',
                'name': 'гарнитура цилиндрична глава',
                'unit': 'бр',
                'quantity': 1.00,
                'purchase_price': 37.65,
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0

        for item_data in test_data:
            article_number = item_data['article_number']
            
            # Check if item already exists
            item, created = Sklad.objects.get_or_create(
                article_number=article_number,
                defaults=item_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {article_number} - {item_data["name"]}')
                )
            else:
                # Update existing item
                for key, value in item_data.items():
                    setattr(item, key, value)
                item.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {article_number} - {item_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created: {created_count}, Updated: {updated_count}'
            )
        )
