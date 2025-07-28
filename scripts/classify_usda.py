def classify_usda(sand, silt, clay):
    if 0 <= sand <= 45 and 40 <= clay <= 100 and 0 <= silt <= 40:
        return 'Cl'  # Clay
    elif 45 <= sand <= 65 and 35 <= clay <= 55 and 0 <= silt <= 20:
        return 'SaCl'  # Sandy Clay
    elif 0 <= sand <= 20 and 40 <= clay <= 60 and 40 <= silt <= 60:
        return 'SiCl'  # Silty Clay
    elif 20 <= sand <= 45 and 25 <= clay <= 40 and 15 <= silt <= 55:
        return 'ClLo'  # Clay Loam
    elif 0 <= sand <= 20 and 25 <= clay <= 40 and 40 <= silt <= 75:
        return 'SiClLo'  # Silty Clay Loam
    elif 45 <= sand <= 80 and 20 <= clay <= 35 and 0 <= silt <= 25:
        return 'SaClLo'  # Sandy Clay Loam
    elif 25 <= sand <= 55 and 5 <= clay <= 25 and 25 <= silt <= 50:
        return 'Lo'  # Loam
    elif 85 <= sand <= 100 and 0 <= clay <= 10 and 0 <= silt <= 15:
        return 'Sa'  # Sand
    elif 70 <= sand <= 90 and 0 <= clay <= 15 and 0 <= silt <= 30:
        return 'LoSa'  # Loamy Sand
    elif 45 <= sand <= 85 and 0 <= clay <= 20 and 0 <= silt <= 50:
        return 'SaLo'  # Sandy Loam
    elif 0 <= sand <= 50 and 0 <= clay <= 25 and 50 <= silt <= 85:
        return 'SiLo'  # Silty Loam
    elif 0 <= sand <= 20 and 0 <= clay <= 15 and 80 <= silt <= 100:
        return 'Si'  # Silt
    else:
        return 'Unk'  # Unknown or outside defined ranges