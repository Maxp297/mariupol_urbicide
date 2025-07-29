import pandas as pd

# Load the original CSV, skipping the index row
source = 'damage_assessment_full.csv'
df = pd.read_csv(source, skiprows=[1])

# Claude forensic schema mapping (customize as needed)
column_map = {
    'Unnamed: 2_level_0 Unnamed: 2_level_1': 'contractor',
    'Unnamed: 4_level_0 Unnamed: 4_level_1': 'responsible_executor',
    'Unnamed: 5_level_0 Unnamed: 5_level_1': 'city',
    'Unnamed: 6_level_0 Unnamed: 6_level_1': 'district',
    'Unnamed: 7_level_0 Unnamed: 7_level_1': 'microdistrict',
    'Unnamed: 8_level_0 Unnamed: 8_level_1': 'street_type',
    'Unnamed: 9_level_0 Unnamed: 9_level_1': 'street_name',
    'Unnamed: 10_level_0 Unnamed: 10_level_1': 'building_number',
    'Unnamed: 11_level_0 Unnamed: 11_level_1': 'full_address',
    'Unnamed: 14_level_0 Unnamed: 14_level_1': 'building_type',
    'Unnamed: 15_level_0 Unnamed: 15_level_1': 'usage',
    'Unnamed: 16_level_0 Unnamed: 16_level_1': 'notes',
    'Unnamed: 17_level_0 Unnamed: 17_level_1': 'damage_notes',
    'Unnamed: 18_level_0 Unnamed: 18_level_1': 'category',
    'Unnamed: 19_level_0 Unnamed: 19_level_1': 'repair_group',
    'Unnamed: 20_level_0 Не проведено': 'not_done',
    'Unnamed: 21_level_0 Снос': 'demolition',
    'Unnamed: 22_level_0 Реконструкция': 'reconstruction',
    'Unnamed: 23_level_0 Ремонт': 'repair',
    'Unnamed: 24_level_0 Этажность': 'num_floors',
    'Unnamed: 25_level_0 Кол-во подъездов': 'num_entrances',
    'Unnamed: 26_level_0 Кол-во квартир': 'num_apartments',
    'Unnamed: 27_level_0 Кол-во мест, шт.': 'num_places',
    'Unnamed: 28_level_0 Строительный объем, куб.м': 'building_volume_m3',
    'Unnamed: 29_level_0 Площадь здания, тыс.кв.м': 'building_area_1',
    'Unnamed: 30_level_0 Площадь здания, тыс.кв.м': 'building_area_2',
    'Unnamed: 31_level_0 Площадь здания, тыс.кв.м': 'building_area_3',
    'Unnamed: 32_level_0 Площадь здания, тыс.кв.м': 'building_area_4',
    'Unnamed: 33_level_0 Площадь здания, тыс.кв.м': 'building_area_5',
    'Unnamed: 34_level_0 Площадь здания, тыс.кв.м': 'building_area_6',
    'Unnamed: 35_level_0 План': 'plan_1',
    'Unnamed: 36_level_0 Факт': 'fact_1',
    'Unnamed: 37_level_0 План': 'plan_2',
    'Unnamed: 38_level_0 Факт': 'fact_2',
    'Unnamed: 39_level_0 Отклонение, %': 'deviation_percent',
    'Unnamed: 40_level_0 План': 'plan_3',
    'Unnamed: 41_level_0 Факт': 'fact_3',
    'Unnamed: 42_level_0 Отклонение, дней': 'deviation_days',
    'Кол-во личного состава, чел. План': 'personnel_plan',
    'Кол-во личного состава, чел. Факт': 'personnel_fact',
    'Кол-во личного состава, чел. Отклонение, %': 'personnel_deviation_percent',
    'Кол-во техники, шт. План': 'equipment_plan',
    'Кол-во техники, шт. Факт': 'equipment_fact',
    'Кол-во техники, шт. Отклонение, %': 'equipment_deviation_percent',
    'Кол-во техники, шт. Отклонение, %.1': 'equipment_deviation_percent_2',
    'Кол-во техники, шт. Отклонение, %.2': 'equipment_deviation_percent_3',
    'Кол-во техники, шт. Общий': 'equipment_total',
    'Кол-во техники, шт. в т.ч. внешних инженерных коммуникаций.2': 'equipment_ext_comm_2',
    'Кол-во техники, шт. в т.ч. внешних инженерных коммуникаций.3': 'equipment_ext_comm_3',
    'Кол-во техники, шт. в т.ч. внешних инженерных коммуникаций.4': 'equipment_ext_comm_4',
}

# Actually rename columns (keep only those mapped)
df = df.rename(columns=column_map)
df = df[list(column_map.values())]

# Remove index/empty rows (if any)
df = df[df['contractor'].notnull()]

# Save cleaned, mapped version
df.to_csv('damage_assessment_clean_en.csv', index=False, encoding='utf-8-sig')

print("Saved as damage_assessment_clean_en.csv with English forensic schema columns.")
