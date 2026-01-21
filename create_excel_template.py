import csv

# Create CSV template with all configuration types
with open('hotel_configurations_template.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header
    writer.writerow(['Type', 'Name', 'Description', 'Max_Occupancy', 'Usage', 'Number', 'Icon'])
    
    # Room Types
    room_types = [
        ['RoomType', 'Standard Room', 'Basic accommodation with essential amenities', '', '', '', ''],
        ['RoomType', 'Deluxe Room', 'Enhanced comfort room with premium features', '', '', '', ''],
        ['RoomType', 'Suite', 'Spacious suite with separate living area', '', '', '', ''],
        ['RoomType', 'Presidential Suite', 'Luxury presidential suite with exclusive services', '', '', '', ''],
        ['RoomType', 'Executive Room', 'Business-focused room with work facilities', '', '', '', ''],
        ['RoomType', 'Family Room', 'Large room designed for families with children', '', '', '', ''],
        ['RoomType', 'Studio Apartment', 'Compact apartment-style accommodation', '', '', '', ''],
        ['RoomType', 'Penthouse Suite', 'Top-floor luxury suite with panoramic views', '', '', '', ''],
        ['RoomType', 'Junior Suite', 'Smaller suite with sitting area', '', '', '', ''],
        ['RoomType', 'Connecting Rooms', 'Adjacent rooms with connecting door', '', '', '', '']
    ]
    
    # Room Categories
    room_categories = [
        ['RoomCategory', 'Economy', 'Budget-friendly option with basic amenities', '2', '', '', ''],
        ['RoomCategory', 'Business', 'Business traveler focused with work facilities', '2', '', '', ''],
        ['RoomCategory', 'Premium', 'Premium experience with enhanced comfort', '4', '', '', ''],
        ['RoomCategory', 'Luxury', 'Ultimate luxury with exclusive services', '6', '', '', ''],
        ['RoomCategory', 'Budget', 'Most affordable accommodation option', '1', '', '', ''],
        ['RoomCategory', 'Comfort', 'Comfortable stay with standard amenities', '2', '', '', ''],
        ['RoomCategory', 'Superior', 'Enhanced comfort with superior features', '3', '', '', ''],
        ['RoomCategory', 'Executive', 'Executive level with business amenities', '4', '', '', ''],
        ['RoomCategory', 'VIP', 'VIP treatment with personalized services', '4', '', '', ''],
        ['RoomCategory', 'Royal', 'Royal treatment with ultimate luxury', '8', '', '', '']
    ]
    
    # Bed Types
    bed_types = [
        ['BedType', 'Single Bed', 'Single occupancy bed for one person', '', 'Single occupancy', '', ''],
        ['BedType', 'Double Bed', 'Standard double bed for two people', '', 'Double occupancy', '', ''],
        ['BedType', 'Queen Bed', 'Queen size bed with extra comfort', '', 'Double occupancy', '', ''],
        ['BedType', 'King Bed', 'King size bed with maximum space', '', 'Double occupancy', '', ''],
        ['BedType', 'Twin Beds', 'Two separate single beds', '', 'Twin occupancy', '', ''],
        ['BedType', 'Bunk Beds', 'Stacked beds for space efficiency', '', 'Bunk occupancy', '', ''],
        ['BedType', 'Sofa Bed', 'Convertible sofa that opens to bed', '', 'Flexible seating/sleeping', '', ''],
        ['BedType', 'Murphy Bed', 'Wall-mounted fold-down bed', '', 'Space-saving sleeping', '', ''],
        ['BedType', 'Daybed', 'Couch-style bed for lounging', '', 'Lounge/sleep combination', '', ''],
        ['BedType', 'Rollaway Bed', 'Portable bed on wheels', '', 'Additional guest sleeping', '', '']
    ]
    
    # Floors
    floors = [
        ['Floor', 'Ground Floor', 'Main entrance level with lobby and reception', '', '', '0', ''],
        ['Floor', 'First Floor', 'First level above ground with standard rooms', '', '', '1', ''],
        ['Floor', 'Second Floor', 'Second level with standard accommodations', '', '', '2', ''],
        ['Floor', 'Third Floor', 'Third level with enhanced room features', '', '', '3', ''],
        ['Floor', 'Fourth Floor', 'Fourth level with premium accommodations', '', '', '4', ''],
        ['Floor', 'Fifth Floor', 'Fifth level with superior room amenities', '', '', '5', ''],
        ['Floor', 'Mezzanine', 'Intermediate floor between ground and first', '', '', '2', ''],
        ['Floor', 'Penthouse', 'Top floor luxury with panoramic views', '', '', '10', ''],
        ['Floor', 'Basement', 'Below ground level for storage/utilities', '', '', '-1', ''],
        ['Floor', 'Rooftop', 'Open-air top level with sky access', '', '', '11', '']
    ]
    
    # Amenities
    amenities = [
        ['Amenity', 'Free Wi-Fi', 'Complimentary high-speed internet access', '', '', '', 'fas fa-wifi'],
        ['Amenity', 'Air Conditioning', 'Climate control for optimal comfort', '', '', '', 'fas fa-snowflake'],
        ['Amenity', 'TV', 'Flat screen television with cable channels', '', '', '', 'fas fa-tv'],
        ['Amenity', 'Mini Bar', 'In-room refrigerated bar with beverages', '', '', '', 'fas fa-glass-martini'],
        ['Amenity', 'Balcony', 'Private outdoor space with seating', '', '', '', 'fas fa-door-open'],
        ['Amenity', 'Work Desk', 'Dedicated workspace with ergonomic chair', '', '', '', 'fas fa-desk'],
        ['Amenity', 'Safe', 'In-room security safe for valuables', '', '', '', 'fas fa-lock'],
        ['Amenity', 'Coffee Machine', 'Coffee and tea making facilities', '', '', '', 'fas fa-coffee'],
        ['Amenity', 'Jacuzzi', 'Private hot tub for relaxation', '', '', '', 'fas fa-hot-tub'],
        ['Amenity', 'Fireplace', 'In-room fireplace for ambiance', '', '', '', 'fas fa-fire'],
        ['Amenity', 'Kitchen', 'Fully equipped kitchenette', '', '', '', 'fas fa-utensils'],
        ['Amenity', 'Washing Machine', 'In-room laundry facilities', '', '', '', 'fas fa-tshirt'],
        ['Amenity', 'Gym Access', 'Complimentary fitness center access', '', '', '', 'fas fa-dumbbell'],
        ['Amenity', 'Pool Access', 'Swimming pool and aquatic facilities', '', '', '', 'fas fa-swimmer'],
        ['Amenity', 'Spa Access', 'Wellness and spa treatment access', '', '', '', 'fas fa-spa'],
        ['Amenity', 'Room Service', '24-hour in-room dining service', '', '', '', 'fas fa-bell'],
        ['Amenity', 'Concierge', 'Personal concierge assistance', '', '', '', 'fas fa-concierge-bell'],
        ['Amenity', 'Valet Parking', 'Professional car parking service', '', '', '', 'fas fa-car'],
        ['Amenity', 'Pet Friendly', 'Welcomes pets with special amenities', '', '', '', 'fas fa-paw'],
        ['Amenity', 'Smoking Allowed', 'Designated smoking-permitted accommodation', '', '', '', 'fas fa-smoking']
    ]
    
    # Write all data
    for row in room_types + room_categories + bed_types + floors + amenities:
        writer.writerow(row)

print("CSV template created: hotel_configurations_template.csv")