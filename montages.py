# montages.py

# ==========================================
# STANDARD 10-20 SYSTEM (19-21 Channels)
# ==========================================
montage_10_20 = {
    'Fp1': (-0.3, 0.95),  'Fpz': (0.0, 0.95),  'Fp2': (0.3, 0.95),
    'F7': (-0.8, 0.6),    'F3': (-0.4, 0.6),   'Fz': (0.0, 0.6),    'F4': (0.4, 0.6),    'F8': (0.8, 0.6),
    'T7': (-0.95, 0.0),   'C3': (-0.4, 0.0),   'Cz': (0.0, 0.0),    'C4': (0.4, 0.0),    'T8': (0.95, 0.0),
    'P7': (-0.8, -0.6),   'P3': (-0.4, -0.6),  'Pz': (0.0, -0.6),   'P4': (0.4, -0.6),   'P8': (0.8, -0.6),
    'O1': (-0.3, -0.95),  'Oz': (0.0, -0.95),  'O2': (0.3, -0.95)
}

# ==========================================
# EXTENDED 10-10 SYSTEM (64 Channels)
# ==========================================
montage_10_10 = {
    # Frontal Pole
    'Fp1': (-0.3, 0.95),  'Fpz': (0.0, 0.95),  'Fp2': (0.3, 0.95),
    # Anterior Frontal
    'AF7': (-0.6, 0.8),   'AF3': (-0.3, 0.8),  'AFz': (0.0, 0.8),   'AF4': (0.3, 0.8),   'AF8': (0.6, 0.8),
    # Frontal
    'F7': (-0.8, 0.6),    'F5': (-0.6, 0.6),   'F3': (-0.4, 0.6),   'F1': (-0.2, 0.6),   
    'Fz': (0.0, 0.6),     'F2': (0.2, 0.6),    'F4': (0.4, 0.6),    'F6': (0.6, 0.6),    'F8': (0.8, 0.6),
    # Frontal-Central
    'FT7': (-0.9, 0.3),   'FC5': (-0.7, 0.3),  'FC3': (-0.4, 0.3),  'FC1': (-0.2, 0.3),  
    'FCz': (0.0, 0.3),    'FC2': (0.2, 0.3),   'FC4': (0.4, 0.3),   'FC6': (0.7, 0.3),   'FT8': (0.9, 0.3),
    # Central
    'T7': (-0.95, 0.0),   'C5': (-0.7, 0.0),   'C3': (-0.4, 0.0),   'C1': (-0.2, 0.0),   
    'Cz': (0.0, 0.0),     'C2': (0.2, 0.0),    'C4': (0.4, 0.0),    'C6': (0.7, 0.0),    'T8': (0.95, 0.0),
    'T9': (-1.05, 0.0),   'T10': (1.05, 0.0), # Lower temporal
    # Central-Parietal
    'TP7': (-0.9, -0.3),  'CP5': (-0.7, -0.3), 'CP3': (-0.4, -0.3), 'CP1': (-0.2, -0.3), 
    'CPz': (0.0, -0.3),   'CP2': (0.2, -0.3),  'CP4': (0.4, -0.3),  'CP6': (0.7, -0.3),  'TP8': (0.9, -0.3),
    # Parietal
    'P7': (-0.8, -0.6),   'P5': (-0.6, -0.6),  'P3': (-0.4, -0.6),  'P1': (-0.2, -0.6),  
    'Pz': (0.0, -0.6),    'P2': (0.2, -0.6),   'P4': (0.4, -0.6),   'P6': (0.6, -0.6),   'P8': (0.8, -0.6),
    # Parieto-Occipital
    'PO7': (-0.6, -0.8),  'PO3': (-0.3, -0.8), 'POz': (0.0, -0.8),  'PO4': (0.3, -0.8),  'PO8': (0.6, -0.8),
    # Occipital & Inion
    'O1': (-0.3, -0.95),  'Oz': (0.0, -0.95),  'O2': (0.3, -0.95),  'Iz': (0.0, -1.05)
}


def get_layout(n_channels: int) -> dict:
    """
    Returns the appropriate montage layout based on the number of channels in the EEG data.
    """
    if n_channels <= 22:
        return montage_10_20
    elif n_channels <= 65:
        return montage_10_10
    else:
        return None
    

def match_channel_name(edf_label: str, montage_dict: dict) -> str:
    """
    Cleans the channel name from the EDF format (e.g., 'Fc5.', 'C3..')
    and matches it to the montage dictionary, ignoring case.
    """
    clean_label = edf_label.replace('.', '').strip().upper()
    
    for key in montage_dict.keys():
        if key.upper() == clean_label:
            return key
    return None