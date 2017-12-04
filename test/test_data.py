import os
import datetime
from decimal import Decimal


class TestData:
    data_location = r'C:\Users\jstembridge\PycharmProjects\wagsv\data'
    events_data = r'2017\events.tab'
    shots_data = r'shots.tab'
    events_file = os.path.join(data_location, events_data)
    shots_file = os.path.join(data_location, shots_data)
    handicaps_file = os.path.join(data_location, 'hcaps.tab')

    example_event_record = {
        'num': '4',
        'date': 'Monday 22 May',
        'venue': 'West Surrey',
        'event': 'The Shutes Shot-Glass',
        'address': 'Enton Green,Godalming,Surrey',
        'post_code': 'GU8 5AF',
        'phone': '01483 421275',
        'member_price': '60',
        'guest_price': '70',
        'schedule': '10.30 Coffee and bacon rolls,11.16 Tee off 18 holes,16.30 1 Course Meal',
        'organiser': 'Anthony Shutes',
        'directions': 'Whether travelling from Guildford or Portsmouth, turn off the A3 at Milford Junction. At the roundabout take the exit onto the A283 (signposted Milford). At the traffic signals turn left onto Portsmouth Road - A3100 (signposted Godalming). At the mini roundabout, turn right onto Church Road - A286 (signposted Midhurst) then immediately turn left onto Station Lane (signposted Milford Station). At Milford Station, go over the rail crossing and carry on for about 800 yards. At Enton Green, proceed straight on and the entrance to the West Surrey Golf Club is immediately on your right.',
        'note': 'If you are using Satellite Navigation, do not turn into Water Lane where there is no access to the club. The main entrance to the club is directly off Station Road.',
        'dinner_price': '',
        'dinner_incl': '',
        'jacket': '',
        'url': 'www.wsgc.co.uk/',
        'deadline': 'Thursday 18 May',
        'max': '24'
    }

    example_event_record_updated = {
        'num': '4',
        'date': 'Monday 22 May',
        'venue': 'West Surrey',
        'event': 'The Shutes Shot-Glass',
        'address': 'Enton Green,Godalming,Surrey',
        'post_code': 'GU8 5AF',
        'phone': '01483 421275',
        'member_price': '25.00',
        'guest_price': '70.00',
        'schedule': '10.30 Coffee and bacon rolls,11.15 Tee off 18 holes,16.00 Buffet',
        'organiser': 'Anthony Shutes',
        'directions': 'Whether travelling from Guildford or Portsmouth, turn off the A3 at Milford Junction. At the roundabout take the exit onto the A283 (signposted Milford). At the traffic signals turn left onto Portsmouth Road - A3100 (signposted Godalming). At the mini roundabout, turn right onto Church Road - A286 (signposted Midhurst) then immediately turn left onto Station Lane (signposted Milford Station). At Milford Station, go over the rail crossing and carry on for about 800 yards. At Enton Green, proceed straight on and the entrance to the West Surrey Golf Club is immediately on your right.',
        'note': '*** New note ***',
        'dinner_price': '',
        'dinner_incl': '',
        'jacket': '',
        'url': 'www.wsgc.co.uk/',
        'deadline': 'Saturday 20 May',
        'max': '24'
    }

    example_event_record_empty = {
        'num': None, 'date': None, 'venue': None, 'event': None, 'address': None, 'post_code': None, 'phone': None, 'member_price': None, 'guest_price': None, 'schedule': None, 'organiser': None, 'directions': None, 'note': None, 'dinner_price': None, 'dinner_incl': None, 'jacket': None, 'url': None, 'deadline': None, 'max': None
    }

    example_event = {
        'num': '4',
        'date': datetime.date(2017, 5, 22),
        'venue': 'West Surrey',
        'event': 'The Shutes Shot-Glass',
        'address': 'Enton Green,Godalming,Surrey',
        'post_code': 'GU8 5AF',
        'phone': '01483 421275',
        'member_price': Decimal("60"),
        'guest_price': Decimal("70"),
        'schedule': [
            {'time': datetime.time(10, 30), 'text': 'Coffee and bacon rolls'},
            {'time': datetime.time(11, 16), 'text': 'Tee off 18 holes'},
            {'time': datetime.time(16, 30), 'text': '1 Course Meal'},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None},
            {'time': datetime.time(0, 0), 'text': None}
        ],
        'organiser': 'Anthony Shutes',
        'directions': 'Whether travelling from Guildford or Portsmouth, turn off the A3 at Milford Junction. At the roundabout take the exit onto the A283 (signposted Milford). At the traffic signals turn left onto Portsmouth Road - A3100 (signposted Godalming). At the mini roundabout, turn right onto Church Road - A286 (signposted Midhurst) then immediately turn left onto Station Lane (signposted Milford Station). At Milford Station, go over the rail crossing and carry on for about 800 yards. At Enton Green, proceed straight on and the entrance to the West Surrey Golf Club is immediately on your right.',
        'dinner_price': '',
        'dinner_incl': '',
        'jacket': '',
        'url': 'www.wsgc.co.uk/',
        'max': '24',
        'end_booking': datetime.date(2017, 5, 18),
        'start_booking': datetime.date(2017, 5, 8),
        'notes': 'If you are using Satellite Navigation, do not turn into Water Lane where there is no access to the club. The main entrance to the club is directly off Station Road.'
    }

    example_event_field = ['Richard Trinick', 'Gerry Robinson', 'John Stembridge', 'Anthony Shutes', 'Richard Latham', 'Mike Dearden', 'Mike Wells', 'Steve Shaw', 'Bob Hill', 'Quintin Heaney', 'Martin Dilke-Wing', 'Richard Latham', 'Peter Berring', 'Gerry McGuffie', 'Rhod James']

    example_course_data_1 = {
         'course': '4', 'year': '3000', 'sss': '70', 'si1': '9', 'si2': '15', 'si3': '3', 'si4': '7', 'si5': '17',
         'si6': '1', 'si7': '13', 'si8': '5', 'si9': '11', 'si10': '12', 'si11': '18', 'si12': '2', 'si13': '16',
         'si14': '8', 'si15': '4', 'si16': '14', 'si17': '6', 'si18': '10', 'par': '70', 'par1': '4', 'par2': '3',
         'par3': '4', 'par4': '3', 'par5': '4', 'par6': '4', 'par7': '3', 'par8': '5', 'par9': '4', 'par10': '3',
         'par11': '4', 'par12': '4', 'par13': '4', 'par14': '3', 'par15': '5', 'par16': '4', 'par17': '5', 'par18': '4'
    }

    example_course_data_2 = {
         'course': '4', 'year': '1997', 'sss': '69', 'si1': '2', 'si2': '16', 'si3': '4', 'si4': '12', 'si5': '18',
         'si6': '8', 'si7': '14', 'si8': '10', 'si9': '6', 'si10': '15', 'si11': '17', 'si12': '7', 'si13': '9',
         'si14': '13', 'si15': '11', 'si16': '1', 'si17': '5', 'si18': '3', 'par': '70', 'par1': '4', 'par2': '3',
         'par3': '4', 'par4': '3', 'par5': '4', 'par6': '4', 'par7': '3', 'par8': '5', 'par9': '4', 'par10': '3',
         'par11': '4', 'par12': '4', 'par13': '4', 'par14': '3', 'par15': '5', 'par16': '4', 'par17': '5', 'par18': '4'
         }

    example_course_data_3 = {
         'course': '21', 'year': '3000', 'sss': '69', 'si1': '6', 'si2': '12', 'si3': '4', 'si4': '14', 'si5': '16',
         'si6': '2', 'si7': '8', 'si8': '18', 'si9': '10', 'si10': '11', 'si11': '1', 'si12': '9', 'si13': '5',
         'si14': '7', 'si15': '17', 'si16': '3', 'si17': '15', 'si18': '13', 'par': '71', 'par1': '4', 'par2': '5',
         'par3': '3', 'par4': '4', 'par5': '3', 'par6': '4', 'par7': '4', 'par8': '3', 'par9': '5', 'par10': '5',
         'par11': '4', 'par12': '4', 'par13': '4', 'par14': '4', 'par15': '3', 'par16': '5', 'par17': '3', 'par18': '4'
    }