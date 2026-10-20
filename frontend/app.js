/**
 * Flying Cabs India Platform — Ola & Uber Bharat Edition
 * Whole India Coverage, Google Maps & Terrain Views, 4-Digit Ride OTP, and Razorpay Payments
 */

// ==========================================================================
// 1. Web Audio API Sound Synthesizer (Zero External Audio File Dependencies)
// ==========================================================================
class SoundSynthesizer {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  play(type) {
    try {
      this.init();
      if (!this.ctx) return;
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.connect(gain);
      gain.connect(this.ctx.destination);

      if (type === 'click') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.05);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.05);
        osc.start(now);
        osc.stop(now + 0.05);
      } else if (type === 'dispatch') {
        // Classic Ola / Uber incoming ride ping
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(750, now);
        osc.frequency.setValueAtTime(950, now + 0.1);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      } else if (type === 'accept') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.08);
        osc.frequency.setValueAtTime(783.99, now + 0.16);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'arrived') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.setValueAtTime(1174.66, now + 0.12);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
        osc.start(now);
        osc.stop(now + 0.4);
      } else if (type === 'otp_verified') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, now);
        osc.frequency.setValueAtTime(880, now + 0.1);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.start(now);
        osc.stop(now + 0.3);
      } else if (type === 'complete') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(659.25, now);
        osc.frequency.setValueAtTime(880, now + 0.12);
        osc.frequency.setValueAtTime(1318.51, now + 0.24);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
        osc.start(now);
        osc.stop(now + 0.6);
      }
    } catch (e) {
      console.warn("Audio play prevented:", e);
    }
  }
}

const sound = new SoundSynthesizer();

// ==========================================================================
// 2. Whole India Metros & Regional Hotspots Data
// ==========================================================================
const CITIES_DATA = {
  all_india: {
    name: "Whole India (Pan-India Overview)",
    center: [21.5937, 78.9629],
    zoom: 5,
    tag: "Pan-India Coverage",
    hotspots: [
      { name: "New Delhi (IGI Airport T3)", lat: 28.5562, lng: 77.1000 },
      { name: "Mumbai (BKC Financial Center)", lat: 19.0760, lng: 72.8777 },
      { name: "Bengaluru (Indiranagar Hub)", lat: 12.9780, lng: 77.6400 },
      { name: "Hyderabad (Hitech City Cyber Towers)", lat: 17.4483, lng: 78.3915 },
      { name: "Kolkata (Park Street)", lat: 22.5726, lng: 88.3639 },
      { name: "Jamshedpur (Sonari Skyport)", lat: 22.8133, lng: 86.1685 }
    ]
  },
  delhi: {
    name: "Delhi NCR (National Capital Region)",
    center: [28.6139, 77.2090],
    zoom: 12,
    tag: "Delhi NCR Corridors Clear",
    hotspots: [
      { name: "Connaught Place (Inner Circle), New Delhi", lat: 28.6304, lng: 77.2177 },
      { name: "Indira Gandhi International Airport (T3)", lat: 28.5562, lng: 77.1000 },
      { name: "Cyber Hub & Cyber City, DLF Gurugram", lat: 28.4952, lng: 77.0890 },
      { name: "Noida Sector 18 Commercial Center", lat: 28.5708, lng: 77.3261 },
      { name: "India Gate & Rajpath Sky Corridor", lat: 28.6129, lng: 77.2295 },
      { name: "New Delhi Railway Station (Ajmeri Gate)", lat: 28.6428, lng: 77.2195 }
    ]
  },
  mumbai: {
    name: "Mumbai (Financial Capital)",
    center: [19.0760, 72.8777],
    zoom: 12,
    tag: "Mumbai Coastal Skyways Active",
    hotspots: [
      { name: "Bandra Kurla Complex (BKC Financial Center)", lat: 19.0657, lng: 72.8687 },
      { name: "Chhatrapati Shivaji Maharaj Airport (T2 BOM)", lat: 19.0896, lng: 72.8656 },
      { name: "Nariman Point & Marine Drive Promenade", lat: 18.9256, lng: 72.8242 },
      { name: "Gateway of India & Colaba Terminal", lat: 18.9220, lng: 72.8346 },
      { name: "Bandra West (Linking Road / Carter Rd)", lat: 19.0607, lng: 72.8362 },
      { name: "Powai IT & Hiranandani Tech Hub", lat: 19.1176, lng: 72.9060 }
    ]
  },
  bengaluru: {
    name: "Bengaluru (Silicon City)",
    center: [12.9716, 77.5946],
    zoom: 12,
    tag: "BLR Sky Corridors Active",
    hotspots: [
      { name: "MG Road Metro & Skyport Terminal, Bengaluru", lat: 12.9756, lng: 77.6066 },
      { name: "Kempegowda International Airport (BLR) Skyport", lat: 13.1986, lng: 77.7066 },
      { name: "Indiranagar 100ft Road Hub", lat: 12.9780, lng: 77.6400 },
      { name: "Whitefield ITPL Tech Corridor", lat: 12.9860, lng: 77.7300 },
      { name: "Silk Board Junction / Koramangala", lat: 12.9170, lng: 77.6220 },
      { name: "Electronic City Phase 1 Skyport", lat: 12.8452, lng: 77.6602 }
    ]
  },
  hyderabad: {
    name: "Hyderabad (Cyberabad)",
    center: [17.3850, 78.4867],
    zoom: 12,
    tag: "Hyd Skyway & Metro Clear",
    hotspots: [
      { name: "Hitech City & Cyber Towers Hub", lat: 17.4483, lng: 78.3915 },
      { name: "Rajiv Gandhi International Airport (RGIA HYD)", lat: 17.2403, lng: 78.4294 },
      { name: "Gachibowli Financial District", lat: 17.4399, lng: 78.3489 },
      { name: "Charminar Heritage Terminal", lat: 17.3616, lng: 78.4747 },
      { name: "Banjara Hills Road No. 1", lat: 17.4156, lng: 78.4350 },
      { name: "Secunderabad Railway Station", lat: 17.4344, lng: 78.5017 }
    ]
  },
  chennai: {
    name: "Chennai (Automotive Hub)",
    center: [13.0827, 80.2707],
    zoom: 12,
    tag: "Chennai Coastal Corridors",
    hotspots: [
      { name: "T. Nagar Commercial Center, Chennai", lat: 13.0418, lng: 80.2341 },
      { name: "Chennai International Airport (MAA)", lat: 12.9941, lng: 80.1709 },
      { name: "Marina Beach Promenade", lat: 13.0500, lng: 80.2824 },
      { name: "OMR IT Expressway / Tidal Park", lat: 12.9880, lng: 80.2470 },
      { name: "Chennai Central Railway Station", lat: 13.0836, lng: 80.2754 }
    ]
  },
  kolkata: {
    name: "Kolkata (City of Joy)",
    center: [22.5726, 88.3639],
    zoom: 12,
    tag: "Kolkata Riverway Active",
    hotspots: [
      { name: "Park Street & Chowringhee Center", lat: 22.5535, lng: 88.3512 },
      { name: "Netaji Subhash Chandra Bose Airport (CCU)", lat: 22.6547, lng: 88.4467 },
      { name: "Salt Lake Sector V IT Hub", lat: 22.5786, lng: 88.4323 },
      { name: "Howrah Railway Station & Bridge", lat: 22.5850, lng: 88.3426 },
      { name: "Victoria Memorial Sky Corridor", lat: 22.5448, lng: 88.3426 }
    ]
  },
  pune: {
    name: "Pune (Oxford of the East)",
    center: [18.5204, 73.8567],
    zoom: 12,
    tag: "Pune Western Skyway Active",
    hotspots: [
      { name: "Hinjewadi IT Park Phase 1", lat: 18.5913, lng: 73.7389 },
      { name: "Pune International Airport (PNQ)", lat: 18.5822, lng: 73.9197 },
      { name: "Koregaon Park & North Main Road", lat: 18.5362, lng: 73.8940 },
      { name: "FC Road & Shivajinagar Center", lat: 18.5284, lng: 73.8443 },
      { name: "Magarpatta Cybercity, Hadapsar", lat: 18.5158, lng: 73.9272 }
    ]
  },
  ahmedabad: {
    name: "Ahmedabad (Sabarmati City)",
    center: [23.0225, 72.5714],
    zoom: 12,
    tag: "Sabarmati Corridors Clear",
    hotspots: [
      { name: "Sabarmati Riverfront Promenade", lat: 23.0300, lng: 72.5750 },
      { name: "Sardar Vallabhbhai Patel Airport (AMD)", lat: 23.0772, lng: 72.6347 },
      { name: "SG Highway IT Corridor", lat: 23.0350, lng: 72.5150 },
      { name: "Gandhinagar GIFT City Skyport", lat: 23.1610, lng: 72.6840 }
    ]
  },
  jaipur: {
    name: "Jaipur (Pink City)",
    center: [26.9124, 75.7873],
    zoom: 12,
    tag: "Jaipur Skyway Clear",
    hotspots: [
      { name: "Hawa Mahal & Old Pink City Center", lat: 26.9239, lng: 75.8267 },
      { name: "Jaipur International Airport (JAI)", lat: 26.8242, lng: 75.8122 },
      { name: "MI Road & C-Scheme Commercial Hub", lat: 26.9160, lng: 75.8080 },
      { name: "Amer Fort Heritage Sky Corridor", lat: 26.9855, lng: 75.8513 }
    ]
  },
  jamshedpur: {
    name: "Jamshedpur (Steel City)",
    center: [22.8046, 86.2029],
    zoom: 13,
    tag: "Steel City Corridors Clear",
    hotspots: [
      { name: "Sonari Airport Skyport (IXW/JLR), Jamshedpur", lat: 22.8133, lng: 86.1685 },
      { name: "Bistupur Commercial Center & Gopal Maidan", lat: 22.8010, lng: 86.1860 },
      { name: "Jubilee Park & Tata Steel Skydeck", lat: 22.8080, lng: 86.2030 },
      { name: "Tatanagar Railway Station Skyport Terminal", lat: 22.7712, lng: 86.2035 },
      { name: "Telco Town & Tata Motors Sky Corridor", lat: 22.7850, lng: 86.2480 },
      { name: "Kadma / Marine Drive Riverfront Helipad", lat: 22.8150, lng: 86.1550 }
    ]
  },
  lucknow: {
    name: "Lucknow (Nawabi Heritage)",
    center: [26.8467, 80.9462],
    zoom: 12,
    tag: "Gomti Sky Corridors Active",
    hotspots: [
      { name: "Hazratganj Heritage Market, Lucknow", lat: 26.8467, lng: 80.9462 },
      { name: "Chaudhary Charan Singh Airport (LKO)", lat: 26.7606, lng: 80.8893 },
      { name: "Gomti Nagar IT City Hub", lat: 26.8500, lng: 81.0000 },
      { name: "Charbagh Railway Station Hub", lat: 26.8300, lng: 80.9200 }
    ]
  },
  chandigarh: {
    name: "Chandigarh (City Beautiful)",
    center: [30.7333, 76.7794],
    zoom: 12,
    tag: "Shivalik Sky Corridors Open",
    hotspots: [
      { name: "Sector 17 City Center Plaza", lat: 30.7398, lng: 76.7827 },
      { name: "Chandigarh International Airport (IXC)", lat: 30.6734, lng: 76.7885 },
      { name: "Sukhna Lake Promenade Hub", lat: 30.7421, lng: 76.8188 },
      { name: "IT Park Technology Corridor", lat: 30.7250, lng: 76.8450 }
    ]
  },
  kochi: {
    name: "Kochi (Queen of Arabian Sea)",
    center: [9.9312, 76.2673],
    zoom: 12,
    tag: "Backwater Skyways Active",
    hotspots: [
      { name: "Marine Drive Promenade, Kochi", lat: 9.9793, lng: 76.2762 },
      { name: "Cochin International Airport (COK)", lat: 10.1518, lng: 76.3930 },
      { name: "Infopark IT Hub, Kakkanad", lat: 10.0100, lng: 76.3600 },
      { name: "Fort Kochi Heritage Skyport", lat: 9.9650, lng: 76.2420 }
    ]
  },
  goa: {
    name: "Goa (Coastal Transit)",
    center: [15.4909, 73.8278],
    zoom: 11,
    tag: "Coastal Sky Corridor Clear",
    hotspots: [
      { name: "Panaji Mandovi Promenade & Skyport", lat: 15.4989, lng: 73.8278 },
      { name: "Dabolim International Airport (GOI)", lat: 15.3800, lng: 73.8314 },
      { name: "Manohar International Airport Mopa (GOX)", lat: 15.7667, lng: 73.8667 },
      { name: "Calangute Beach Central Hub", lat: 15.5400, lng: 73.7550 }
    ]
  },
  indore: {
    name: "Indore (Cleanest City)",
    center: [22.7196, 75.8577],
    zoom: 12,
    tag: "Malwa Transit Corridors Active",
    hotspots: [
      { name: "Vijay Nagar AB Road Square", lat: 22.7533, lng: 75.8937 },
      { name: "Devi Ahilya Bai Holkar Airport (IDR)", lat: 22.7217, lng: 75.8011 },
      { name: "Rajwada Palace Heritage Hub", lat: 22.7180, lng: 75.8550 },
      { name: "Super Corridor Tech Park", lat: 22.7750, lng: 75.8200 }
    ]
  },
  patna: {
    name: "Patna (Pataliputra Hub)",
    center: [25.5941, 85.1376],
    zoom: 12,
    tag: "Ganga Sky Corridors Clear",
    hotspots: [
      { name: "Gandhi Maidan & Fraser Road Hub", lat: 25.6174, lng: 85.1432 },
      { name: "Jay Prakash Narayan Airport (PAT)", lat: 25.5913, lng: 85.0880 },
      { name: "Patna Junction Railway Station", lat: 25.6020, lng: 85.1370 }
    ]
  },
  bhopal: {
    name: "Bhopal (City of Lakes)",
    center: [23.2599, 77.4126],
    zoom: 12,
    tag: "Bhoj Sky Corridor Active",
    hotspots: [
      { name: "Upper Lake VIP Road Promenade", lat: 23.2500, lng: 77.3800 },
      { name: "Raja Bhoj Airport (BHO)", lat: 23.2875, lng: 77.3378 },
      { name: "MP Nagar Commercial Center", lat: 23.2330, lng: 77.4330 }
    ]
  },
  guwahati: {
    name: "Guwahati (Gateway to North East)",
    center: [26.1445, 91.7362],
    zoom: 12,
    tag: "Brahmaputra Skyways Active",
    hotspots: [
      { name: "GS Road Commercial Hub, Guwahati", lat: 26.1445, lng: 91.7362 },
      { name: "Lokpriya Gopinath Bordoloi Airport (GAU)", lat: 26.1061, lng: 91.5859 },
      { name: "Paltan Bazaar & Guwahati Railway Station", lat: 26.1800, lng: 91.7500 }
    ]
  },
  srinagar: {
    name: "Srinagar (Kashmir Valley)",
    center: [34.0837, 74.7973],
    zoom: 12,
    tag: "Himalayan Skyways Clear",
    hotspots: [
      { name: "Lal Chowk Historic Center", lat: 34.0700, lng: 74.8100 },
      { name: "Dal Lake Boulevard & Skyport", lat: 34.0837, lng: 74.8390 },
      { name: "Sheikh ul-Alam International Airport (SXR)", lat: 33.9870, lng: 74.7740 }
    ]
  },
  varanasi: {
    name: "Varanasi (Spiritual Ghats)",
    center: [25.3176, 82.9739],
    zoom: 12,
    tag: "Kashi Sky Corridors Active",
    hotspots: [
      { name: "Dashashwamedh Ghat & Kashi Vishwanath", lat: 25.3076, lng: 83.0107 },
      { name: "Lal Bahadur Shastri Airport (VNS)", lat: 25.4524, lng: 82.8593 },
      { name: "Banaras Hindu University (BHU) Skyport", lat: 25.2677, lng: 82.9913 }
    ]
  }
};

// ==========================================================================
// 2B. Pan-India Curated Location Index for Live Autocomplete
// ==========================================================================
const INDIAN_LOCATIONS_INDEX = [
  // Curated Pan-India Postal PIN Codes
  { name: "560001 - Sampangirama Nagar / MG Road, Bengaluru", sub: "Bengaluru Central, Karnataka", lat: 12.9797, lng: 77.5947, icon: "📮", category: "pincode", pincode: "560001" },
  { name: "560038 - Indiranagar 100ft Rd / CMH Rd, Bengaluru", sub: "Bengaluru East, Karnataka", lat: 12.9784, lng: 77.6408, icon: "📮", category: "pincode", pincode: "560038" },
  { name: "110001 - Connaught Place / Janpath / India Gate, New Delhi", sub: "Central Delhi, Delhi", lat: 28.6293, lng: 77.2189, icon: "📮", category: "pincode", pincode: "110001" },
  { name: "400001 - Fort / CSMT / Ballard Estate, South Mumbai", sub: "Mumbai City, Maharashtra", lat: 18.9400, lng: 72.8353, icon: "📮", category: "pincode", pincode: "400001" },
  { name: "500081 - HITEC City / Cyber Towers / Madhapur, Hyderabad", sub: "Rangareddy, Telangana", lat: 17.4483, lng: 78.3915, icon: "📮", category: "pincode", pincode: "500081" },
  { name: "600027 - Chennai International Airport (MAA), Meenambakkam", sub: "Chennai, Tamil Nadu", lat: 12.9941, lng: 80.1709, icon: "📮", category: "pincode", pincode: "600027" },
  { name: "700091 - Salt Lake Sector V IT Corridor, Kolkata", sub: "North 24 Parganas, WB", lat: 22.5804, lng: 88.4326, icon: "📮", category: "pincode", pincode: "700091" },
  { name: "411057 - Hinjewadi IT Park Phase 1-3, Pune", sub: "Pune, Maharashtra", lat: 18.5913, lng: 73.7389, icon: "📮", category: "pincode", pincode: "411057" },
  { name: "122002 - DLF Cyber City / Cyber Hub, Gurugram", sub: "Gurugram, Haryana", lat: 28.4829, lng: 77.0920, icon: "📮", category: "pincode", pincode: "122002" },
  { name: "201301 - Sector 18 & Atta Market, Noida", sub: "Gautam Buddha Nagar, UP", lat: 28.5708, lng: 77.3261, icon: "📮", category: "pincode", pincode: "201301" },

  // Delhi NCR
  { name: "Connaught Place (Inner Circle), New Delhi", sub: "Central Delhi, Delhi NCR", lat: 28.6304, lng: 77.2177, icon: "🏛️", pincode: "110001" },
  { name: "Indira Gandhi International Airport (T3 IGI)", sub: "Palam, New Delhi", lat: 28.5562, lng: 77.1000, icon: "✈️", pincode: "110037" },
  { name: "DLF Cyber City & Cyber Hub, Gurugram", sub: "Gurgaon, Haryana", lat: 28.4952, lng: 77.0890, icon: "🏢", pincode: "122002" },
  { name: "Noida Sector 18 Commercial Market", sub: "Noida, Uttar Pradesh", lat: 28.5708, lng: 77.3261, icon: "🛍️", pincode: "201301" },
  { name: "India Gate & Kartavya Path Skyway", sub: "New Delhi", lat: 28.6129, lng: 77.2295, icon: "🇮🇳", pincode: "110001" },
  { name: "Hauz Khas Village & Social Hub", sub: "South Delhi", lat: 28.5494, lng: 77.2001, icon: "☕", pincode: "110016" },
  { name: "New Delhi Railway Station (NDLS)", sub: "Paharganj, New Delhi", lat: 28.6428, lng: 77.2195, icon: "🚉", pincode: "110002" },

  // Mumbai
  { name: "Bandra Kurla Complex (BKC Financial Hub)", sub: "Bandra East, Mumbai", lat: 19.0657, lng: 72.8687, icon: "💼", pincode: "400051" },
  { name: "Chhatrapati Shivaji Maharaj Airport (T2 BOM)", sub: "Sahar, Andheri East, Mumbai", lat: 19.0896, lng: 72.8656, icon: "✈️", pincode: "400099" },
  { name: "Marine Drive & Nariman Point Promenade", sub: "South Mumbai, Maharashtra", lat: 18.9256, lng: 72.8242, icon: "🌊", pincode: "400020" },
  { name: "Gateway of India & Colaba Causeway", sub: "Colaba, Mumbai", lat: 18.9220, lng: 72.8346, icon: "⚓", pincode: "400001" },
  { name: "Powai Hiranandani IT Tech Park", sub: "Powai, Mumbai", lat: 19.1176, lng: 72.9060, icon: "💻", pincode: "400076" },
  { name: "Linking Road & Carter Road Promenade", sub: "Bandra West, Mumbai", lat: 19.0607, lng: 72.8362, icon: "🌴", pincode: "400050" },

  // Bengaluru
  { name: "MG Road Metro & Skyport Terminal", sub: "Central Business District, Bengaluru", lat: 12.9756, lng: 77.6066, icon: "🚇" },
  { name: "Kempegowda International Airport (BLR)", sub: "Devanahalli, Bengaluru", lat: 13.1986, lng: 77.7066, icon: "✈️" },
  { name: "Indiranagar 100ft Road Hub", sub: "Indiranagar, Bengaluru", lat: 12.9780, lng: 77.6400, icon: "🍻" },
  { name: "Whitefield ITPL Technology Corridor", sub: "Whitefield, Bengaluru", lat: 12.9860, lng: 77.7300, icon: "🏢" },
  { name: "Koramangala 80ft Road & Sony Signal", sub: "Koramangala, Bengaluru", lat: 12.9352, lng: 77.6245, icon: "🛍️" },
  { name: "Electronic City Phase 1 Tollway Hub", sub: "Electronic City, Bengaluru", lat: 12.8452, lng: 77.6602, icon: "⚡" },

  // Hyderabad
  { name: "Hitech City & Cyber Towers Hub", sub: "Madhapur, Hyderabad", lat: 17.4483, lng: 78.3915, icon: "💻" },
  { name: "Rajiv Gandhi International Airport (RGIA HYD)", sub: "Shamshabad, Hyderabad", lat: 17.2403, lng: 78.4294, icon: "✈️" },
  { name: "Gachibowli Financial District Hub", sub: "Gachibowli, Hyderabad", lat: 17.4399, lng: 78.3489, icon: "🏢" },
  { name: "Charminar Heritage & Old City", sub: "Old City, Hyderabad", lat: 17.3616, lng: 78.4747, icon: "🕌" },
  { name: "Banjara Hills Road No 12", sub: "Banjara Hills, Hyderabad", lat: 17.4156, lng: 78.4350, icon: "✨" },

  // Kolkata
  { name: "Park Street & Camac Street Hub", sub: "Central Kolkata, West Bengal", lat: 22.5535, lng: 88.3524, icon: "🎷" },
  { name: "Netaji Subhash Chandra Bose Airport (CCU)", sub: "Dum Dum, Kolkata", lat: 22.6547, lng: 88.4467, icon: "✈️" },
  { name: "Salt Lake Sector V IT Corridor", sub: "Salt Lake, Kolkata", lat: 22.5804, lng: 88.4326, icon: "💻" },
  { name: "Howrah Railway Station & Bridge", sub: "Howrah, West Bengal", lat: 22.5838, lng: 88.3426, icon: "🌉" },
  { name: "Victoria Memorial & Maidan", sub: "Maidan, Kolkata", lat: 22.5448, lng: 88.3426, icon: "🏛️" },

  // Chennai
  { name: "Marina Beach Promenade & Skyport", sub: "Triplicane, Chennai", lat: 13.0475, lng: 80.2824, icon: "🏖️" },
  { name: "Chennai International Airport (MAA)", sub: "Meenambakkam, Chennai", lat: 12.9941, lng: 80.1709, icon: "✈️" },
  { name: "OMR IT Corridor & Tidel Park", sub: "Taramani, Chennai", lat: 12.9866, lng: 80.2435, icon: "💻" },
  { name: "T. Nagar Ranganathan Street Commercial Hub", sub: "T. Nagar, Chennai", lat: 13.0418, lng: 80.2341, icon: "🛍️" },

  // Pune
  { name: "Hinjewadi IT Park Phase 1", sub: "Hinjawadi, Pune", lat: 18.5913, lng: 73.7389, icon: "💻" },
  { name: "Pune International Airport (PNQ)", sub: "Lohegaon, Pune", lat: 18.5822, lng: 73.9197, icon: "✈️" },
  { name: "Koregaon Park North Main Road", sub: "Koregaon Park, Pune", lat: 18.5362, lng: 73.8940, icon: "🍃" },

  // Ahmedabad
  { name: "Sabarmati Riverfront Promenade", sub: "Ashram Road, Ahmedabad", lat: 23.0338, lng: 72.5850, icon: "🪁" },
  { name: "Sardar Vallabhbhai Patel Airport (AMD)", sub: "Hansol, Ahmedabad", lat: 23.0734, lng: 72.6266, icon: "✈️" },
  { name: "GIFT City Financial Gateway", sub: "Gandhinagar, Gujarat", lat: 23.1600, lng: 72.6840, icon: "💎" },

  // Jaipur
  { name: "Hawa Mahal & Pink City Walled Quarter", sub: "Badi Choupad, Jaipur", lat: 26.9239, lng: 75.8267, icon: "🦚" },
  { name: "Jaipur International Airport (JAI)", sub: "Sanganer, Jaipur", lat: 26.8289, lng: 75.8056, icon: "✈️" },

  // Jamshedpur
  { name: "Bistupur Main Road & Commercial Center", sub: "Bistupur, Jamshedpur, Jharkhand", lat: 22.8016, lng: 86.1854, icon: "🏭" },
  { name: "Sonari Skyport & Airport Terminal", sub: "Sonari, Jamshedpur", lat: 22.8133, lng: 86.1685, icon: "🛸" },
  { name: "Jubilee Park & Sakchi Hub", sub: "Sakchi, Jamshedpur", lat: 22.8046, lng: 86.2029, icon: "🌳" },
  { name: "Tatanagar Junction Railway Station", sub: "Khasmahal, Jamshedpur", lat: 22.7699, lng: 86.2023, icon: "🚉" },

  // Lucknow
  { name: "Hazratganj Heritage Market", sub: "Hazratganj, Lucknow, UP", lat: 26.8467, lng: 80.9462, icon: "🪔" },
  { name: "Chaudhary Charan Singh Airport (LKO)", sub: "Amausi, Lucknow", lat: 26.7606, lng: 80.8893, icon: "✈️" },

  // Chandigarh
  { name: "Sector 17 City Center Plaza", sub: "Sector 17, Chandigarh", lat: 30.7398, lng: 76.7827, icon: "🌲" },
  { name: "Sukhna Lake Promenade", sub: "Sector 1, Chandigarh", lat: 30.7421, lng: 76.8188, icon: "⛵" },

  // Kochi
  { name: "Marine Drive & Rainbow Bridge", sub: "Ernakulam, Kochi, Kerala", lat: 9.9793, lng: 76.2762, icon: "🌴" },
  { name: "Cochin International Airport (COK)", sub: "Nedumbassery, Kochi", lat: 10.1518, lng: 76.3930, icon: "✈️" },

  // Goa
  { name: "Panaji Mandovi Promenade & Floating Skyport", sub: "Panaji, Goa", lat: 15.4989, lng: 73.8278, icon: "🏖️" },
  { name: "Dabolim International Airport (GOI)", sub: "Dabolim, Goa", lat: 15.3800, lng: 73.8314, icon: "✈️" },

  // Indore
  { name: "Vijay Nagar AB Road Square", sub: "Vijay Nagar, Indore, MP", lat: 22.7533, lng: 75.8937, icon: "🍽️" },
  { name: "Devi Ahilya Bai Holkar Airport (IDR)", sub: "Indore, Madhya Pradesh", lat: 22.7217, lng: 75.8011, icon: "✈️" },

  // Patna
  { name: "Gandhi Maidan & Fraser Road", sub: "Patna, Bihar", lat: 25.6174, lng: 85.1432, icon: "📜" },
  { name: "Jay Prakash Narayan Airport (PAT)", sub: "Patna, Bihar", lat: 25.5913, lng: 85.0880, icon: "✈️" },

  // Bhopal
  { name: "Upper Lake VIP Road Promenade", sub: "Bhopal, Madhya Pradesh", lat: 23.2500, lng: 77.3800, icon: "🏞️" },

  // Guwahati
  { name: "GS Road Commercial Hub", sub: "Dispur, Guwahati, Assam", lat: 26.1445, lng: 91.7362, icon: "🦏" },
  { name: "Lokpriya Gopinath Bordoloi Airport (GAU)", sub: "Borjhar, Guwahati", lat: 26.1061, lng: 91.5859, icon: "✈️" },

  // Srinagar
  { name: "Lal Chowk Historic Center", sub: "Srinagar, Jammu & Kashmir", lat: 34.0700, lng: 74.8100, icon: "🏔️" },
  { name: "Dal Lake Boulevard Skyport", sub: "Srinagar, Kashmir", lat: 34.0837, lng: 74.8390, icon: "🛶" },

  // Varanasi
  { name: "Dashashwamedh Ghat & Kashi Vishwanath", sub: "Varanasi, Uttar Pradesh", lat: 25.3076, lng: 83.0107, icon: "🕉️" },
  { name: "Lal Bahadur Shastri Airport (VNS)", sub: "Babatpur, Varanasi", lat: 25.4524, lng: 82.8593, icon: "✈️" }
];

let defaultUser = {
  id: 1,
  name: "Aarav Sharma",
  role: "rider",
  email: "aarav.sharma@aerocabs.in",
  phone: "+91 98765 43210",
  profile_pic: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
  rating_avg: 4.95
};
try {
  const cached = localStorage.getItem('flying_cabs_user');
  if (cached) defaultUser = JSON.parse(cached);
} catch (e) {}

const state = {
  currentCity: "bengaluru",
  currentMode: defaultUser.role === 'driver' ? 'driver' : 'rider',
  user: defaultUser,
  activeDriver: { id: 1, name: "Capt. Vikram Rathore", vehicle: "AeroVTOL Sky-X7 (Air Garuda)" },
  pickup: {
    name: "MG Road Metro & Skyport Terminal, Bengaluru",
    lat: 12.9756,
    lng: 77.6066
  },
  drop: {
    name: "Kempegowda International Airport (BLR) Skyport",
    lat: 13.1986,
    lng: 77.7066
  },
  selectedTier: "standard", // auto, micro, standard, luxury, bike, flying
  paymentMode: "razorpay", // razorpay, cash
  estimates: null,
  activeRide: null,
  currentRideOtp: "4829",
  autoSimulate: true,
  driverOnline: true,
  pickMode: null, // 'pickup' or 'drop'
  socket: null,
  dispatchTimerInterval: null,
  apiConfig: {
    google_maps_api_key: "AIzaSyA_DemoGoogleMapsKey_FlyingCabsIndia_2026",
    google_maps_map_type: "terrain",
    razorpay_key_id: "rzp_test_1DP5mmOlF5G5ag",
    razorpay_currency: "INR",
    merchant_name: "Flying Cabs (Ola-Uber India)"
  }
};

// ==========================================================================
// 3B. Universal Reverse Geocoding Helper
// ==========================================================================
async function reverseGeocodeLocation(lat, lng) {
  try {
    const res = await fetch(`/api/locations/reverse?lat=${lat}&lng=${lng}`);
    if (res.ok) {
      const data = await res.json();
      if (data && data.name) return data;
    }
  } catch (e) {}
  return { name: `Location [${lat.toFixed(4)}, ${lng.toFixed(4)}]`, sub: "India", lat, lng, icon: "📍" };
}

// ==========================================================================
// 4. Universal Map Manager (Google Maps JS API + Terrain + Leaflet Fallback)
// ==========================================================================
class MapManager {
  constructor() {
    this.mapType = "leaflet"; // 'google' or 'leaflet'
    this.leafletMap = null;
    this.googleMap = null;
    this.markers = {
      pickup: null,
      drop: null,
      driver: null,
      fleet: new Map()
    };
    this.routeLine = null;
    this.googleRouteLine = null;
    this.googleMarkers = {
      pickup: null,
      drop: null,
      driver: null,
      fleet: new Map()
    };
    this.activeTileLayer = null;
  }

  async init() {
    // 1. Fetch live API keys from backend
    try {
      const res = await fetch('/api/rides/config/keys');
      if (res.ok) {
        state.apiConfig = await res.json();
        updateConfigModalInputs();
      }
    } catch (e) {
      console.warn("Could not load backend API keys, using defaults:", e);
    }

    // 2. Initialize Leaflet Map
    this.initLeaflet();

    // 3. Try to dynamically load Google Maps JavaScript API with Terrain
    this.tryLoadGoogleMaps();
  }

  initLeaflet() {
    const defaultCenter = CITIES_DATA[state.currentCity].center;
    const defaultZoom = CITIES_DATA[state.currentCity].zoom;

    this.leafletMap = L.map('leaflet-map', {
      zoomControl: false,
      attributionControl: false
    }).setView(defaultCenter, defaultZoom);

    L.control.zoom({ position: 'bottomright' }).addTo(this.leafletMap);

    // High definition Topographical Relief Terrain layer
    this.setLeafletStyle('terrain');

    // Click handler for picking origin/destination
    this.leafletMap.on('click', (e) => {
      sound.play('click');
      const { lat, lng } = e.latlng;
      const flat = parseFloat(lat.toFixed(5));
      const flng = parseFloat(lng.toFixed(5));

      if (state.pickMode === 'pickup') {
        state.pickup = {
          name: `Pickup [${flat.toFixed(4)}, ${flng.toFixed(4)}]`,
          lat: flat,
          lng: flng
        };
        const pickupInp = document.getElementById('pickup-input');
        pickupInp.value = state.pickup.name;
        state.pickMode = null;
        document.getElementById('btn-pick-origin').classList.remove('active-pick');
        const pClear = document.getElementById('btn-clear-pickup');
        if (pClear) pClear.classList.remove('hidden');
        this.updatePickupDropMarkers();
        fetchFareEstimate();
        fetchNearbyDrivers();
        showToast("📍 Pickup marked! Resolving address...", "info");

        reverseGeocodeLocation(flat, flng).then(geo => {
          if (geo && geo.name) {
            state.pickup.name = geo.name;
            pickupInp.value = geo.name;
            this.updatePickupDropMarkers();
            showToast(`📍 Pickup set to ${geo.name.split(',')[0]}`, "info");
          }
        });
      } else if (state.pickMode === 'drop') {
        state.drop = {
          name: `Destination [${flat.toFixed(4)}, ${flng.toFixed(4)}]`,
          lat: flat,
          lng: flng
        };
        const dropInp = document.getElementById('drop-input');
        dropInp.value = state.drop.name;
        state.pickMode = null;
        document.getElementById('btn-pick-dest').classList.remove('active-pick');
        const dClear = document.getElementById('btn-clear-drop');
        if (dClear) dClear.classList.remove('hidden');
        this.updatePickupDropMarkers();
        fetchFareEstimate();
        fetchNearbyDrivers();
        showToast("🎯 Destination marked! Resolving address...", "info");

        reverseGeocodeLocation(flat, flng).then(geo => {
          if (geo && geo.name) {
            state.drop.name = geo.name;
            dropInp.value = geo.name;
            this.updatePickupDropMarkers();
            showToast(`🎯 Destination set to ${geo.name.split(',')[0]}`, "info");
          }
        });
      }
    });

    this.updatePickupDropMarkers();
  }

  setLeafletStyle(styleKey) {
    if (!this.leafletMap) return;
    if (this.activeTileLayer) {
      this.leafletMap.removeLayer(this.activeTileLayer);
    }

    let url = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    let maxZoom = 19;

    if (styleKey === 'terrain' || styleKey === 'topo_terrain') {
      // Topographical terrain tiles (elevations, hillshades, contours)
      url = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
      maxZoom = 17;
    } else if (styleKey === 'uber_clean') {
      // Clean high-contrast street map
      url = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    } else if (styleKey === 'ola_dark') {
      // Dark transit map
      url = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
    } else if (styleKey === 'satellite') {
      // Satellite imagery
      url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    }

    this.activeTileLayer = L.tileLayer(url, {
      maxZoom: maxZoom,
      subdomains: ['a', 'b', 'c']
    }).addTo(this.leafletMap);
  }

  tryLoadGoogleMaps() {
    const key = state.apiConfig.google_maps_api_key;
    if (!key || key.includes("Demo") || key.includes("mock") || key.length < 25) {
      console.log("Using Topographical Relief Map engine with nationwide vector layers.");
      return;
    }

    // If a valid custom Google Maps API key is configured, dynamically inject script
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=geometry,places&callback=initGoogleMapEngine`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      console.warn("Google Maps script failed to load. Staying on Topographic Terrain engine.");
    };
    window.initGoogleMapEngine = () => {
      this.setupGoogleMapInstance();
    };
    document.head.appendChild(script);
  }

  setupGoogleMapInstance() {
    if (!window.google || !window.google.maps) return;
    try {
      const gEl = document.getElementById('google-map');
      const lEl = document.getElementById('leaflet-map');
      gEl.classList.remove('hidden');
      lEl.classList.add('hidden');
      this.mapType = "google";

      const center = CITIES_DATA[state.currentCity].center;
      this.googleMap = new google.maps.Map(gEl, {
        center: { lat: center[0], lng: center[1] },
        zoom: CITIES_DATA[state.currentCity].zoom,
        mapTypeId: google.maps.MapTypeId.TERRAIN, // Google Maps Terrain layer
        disableDefaultUI: false,
        zoomControl: true,
        streetViewControl: false
      });

      this.googleMap.addListener('click', (e) => {
        sound.play('click');
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        const flat = parseFloat(lat.toFixed(5));
        const flng = parseFloat(lng.toFixed(5));
        if (state.pickMode === 'pickup') {
          state.pickup = {
            name: `Pickup Point [${flat.toFixed(4)}, ${flng.toFixed(4)}]`,
            lat: flat,
            lng: flng
          };
          const pickupInp = document.getElementById('pickup-input');
          pickupInp.value = state.pickup.name;
          state.pickMode = null;
          document.getElementById('btn-pick-origin').classList.remove('active-pick');
          const pClear = document.getElementById('btn-clear-pickup');
          if (pClear) pClear.classList.remove('hidden');
          this.updatePickupDropMarkers();
          fetchFareEstimate();
          fetchNearbyDrivers();
          reverseGeocodeLocation(flat, flng).then(geo => {
            if (geo && geo.name) {
              state.pickup.name = geo.name;
              pickupInp.value = geo.name;
              this.updatePickupDropMarkers();
            }
          });
        } else if (state.pickMode === 'drop') {
          state.drop = {
            name: `Drop Point [${flat.toFixed(4)}, ${flng.toFixed(4)}]`,
            lat: flat,
            lng: flng
          };
          const dropInp = document.getElementById('drop-input');
          dropInp.value = state.drop.name;
          state.pickMode = null;
          document.getElementById('btn-pick-dest').classList.remove('active-pick');
          const dClear = document.getElementById('btn-clear-drop');
          if (dClear) dClear.classList.remove('hidden');
          this.updatePickupDropMarkers();
          fetchFareEstimate();
          fetchNearbyDrivers();
          reverseGeocodeLocation(flat, flng).then(geo => {
            if (geo && geo.name) {
              state.drop.name = geo.name;
              dropInp.value = geo.name;
              this.updatePickupDropMarkers();
            }
          });
        }
      });

      this.updatePickupDropMarkers();
      showToast("⛰️ Google Maps Terrain API Active", "success");
    } catch (err) {
      console.warn("Google Maps init error, falling back to Topo Relief:", err);
    }
  }

  updatePickupDropMarkers() {
    const p = state.pickup;
    const d = state.drop;

    // --- 1. Leaflet Update ---
    if (this.leafletMap) {
      if (this.markers.pickup) this.leafletMap.removeLayer(this.markers.pickup);
      if (this.markers.drop) this.leafletMap.removeLayer(this.markers.drop);

      const pickupIcon = L.divIcon({
        className: 'custom-map-pin pin-pickup',
        html: `<div class="pin-halo"></div><div class="pin-dot">🟢</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });
      const dropIcon = L.divIcon({
        className: 'custom-map-pin pin-drop',
        html: `<div class="pin-halo-drop"></div><div class="pin-dot">🎯</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      this.markers.pickup = L.marker([p.lat, p.lng], { icon: pickupIcon })
        .addTo(this.leafletMap)
        .bindPopup(`<b>Pickup:</b> ${p.name}`);

      this.markers.drop = L.marker([d.lat, d.lng], { icon: dropIcon })
        .addTo(this.leafletMap)
        .bindPopup(`<b>Dropoff:</b> ${d.name}`);

      // Route vector line
      if (this.routeLine) this.leafletMap.removeLayer(this.routeLine);
      const isFlying = state.selectedTier === 'flying';
      this.routeLine = L.polyline([[p.lat, p.lng], [d.lat, d.lng]], {
        color: isFlying ? '#00f0ff' : '#12d878',
        weight: isFlying ? 4 : 5,
        opacity: 0.9,
        dashArray: isFlying ? '8, 8' : null
      }).addTo(this.leafletMap);
    }

    // --- 2. Google Maps Update (if active) ---
    if (this.googleMap && window.google) {
      if (this.googleMarkers.pickup) this.googleMarkers.pickup.setMap(null);
      if (this.googleMarkers.drop) this.googleMarkers.drop.setMap(null);

      this.googleMarkers.pickup = new google.maps.Marker({
        position: { lat: p.lat, lng: p.lng },
        map: this.googleMap,
        title: `Pickup: ${p.name}`
      });

      this.googleMarkers.drop = new google.maps.Marker({
        position: { lat: d.lat, lng: d.lng },
        map: this.googleMap,
        title: `Dropoff: ${d.name}`
      });

      if (this.googleRouteLine) this.googleRouteLine.setMap(null);
      this.googleRouteLine = new google.maps.Polyline({
        path: [{ lat: p.lat, lng: p.lng }, { lat: d.lat, lng: d.lng }],
        strokeColor: state.selectedTier === 'flying' ? '#00f0ff' : '#12d878',
        strokeOpacity: 0.85,
        strokeWeight: 4,
        map: this.googleMap
      });
    }
  }

  updateDriverMarker(lat, lng, altitude, vehicleType, plate) {
    if (this.leafletMap) {
      if (this.markers.driver) {
        this.markers.driver.setLatLng([lat, lng]);
      } else {
        const iconChar = vehicleType === 'flying' ? '🛸' : (vehicleType === 'auto' ? '🛺' : (vehicleType === 'bike' ? '🏍️' : '🚖'));
        const driverIcon = L.divIcon({
          className: 'custom-driver-marker',
          html: `<div class="driver-ping-ring"></div><div class="driver-pin-icon">${iconChar}</div>`,
          iconSize: [40, 40],
          iconAnchor: [20, 20]
        });
        this.markers.driver = L.marker([lat, lng], { icon: driverIcon, zIndexOffset: 1000 }).addTo(this.leafletMap);
      }
    }

    if (this.googleMap && window.google) {
      if (this.googleMarkers.driver) {
        this.googleMarkers.driver.setPosition({ lat, lng });
      } else {
        this.googleMarkers.driver = new google.maps.Marker({
          position: { lat, lng },
          map: this.googleMap,
          title: `Cab: ${plate}`
        });
      }
    }
  }

  renderFleetMarkers(drivers) {
    if (!this.leafletMap) return;

    // Remove old fleet markers
    this.markers.fleet.forEach(m => this.leafletMap.removeLayer(m));
    this.markers.fleet.clear();

    drivers.forEach(d => {
      const iconChar = d.vehicle_type === 'flying' ? '🛸' : (d.vehicle_type === 'auto' ? '🛺' : (d.vehicle_type === 'bike' ? '🏍️' : '🚖'));
      const fIcon = L.divIcon({
        className: 'fleet-marker',
        html: `<div class="f-pin">${iconChar}</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });
      const marker = L.marker([d.current_lat, d.current_lng], { icon: fIcon })
        .addTo(this.leafletMap)
        .bindPopup(`<b>${d.vehicle_info}</b><br>Plate: ${d.license_plate}<br>Status: ${d.status.toUpperCase()}`);
      this.markers.fleet.set(d.id, marker);
    });
  }

  centerCity(cityKey) {
    const city = CITIES_DATA[cityKey];
    if (!city) return;
    if (this.leafletMap) {
      this.leafletMap.flyTo(city.center, city.zoom, { duration: 1.4 });
    }
    if (this.googleMap) {
      this.googleMap.panTo({ lat: city.center[0], lng: city.center[1] });
      this.googleMap.setZoom(city.zoom);
    }
  }

  viewWholeIndia() {
    if (this.leafletMap) {
      // Bounds covering Jammu & Kashmir, Kanyakumari, Gujarat to Assam
      this.leafletMap.flyToBounds([
        [8.0, 68.0],
        [37.5, 97.5]
      ], { duration: 1.5 });
    }
    if (this.googleMap) {
      this.googleMap.setCenter({ lat: 21.5937, lng: 78.9629 });
      this.googleMap.setZoom(5);
    }
    showToast("🇮🇳 Displaying Whole Indian Map", "info");
  }
}

const mapMgr = new MapManager();

// ==========================================================================
// 5. City & Hotspot Switcher
// ==========================================================================
function setCity(cityKey) {
  state.currentCity = cityKey;
  const city = CITIES_DATA[cityKey];
  if (!city) return;

  // Update header and panel texts
  const heading = document.getElementById('panel-city-heading');
  const subtext = document.getElementById('panel-city-subtext');
  const netTag = document.getElementById('network-status-tag');
  const chipLabel = document.getElementById('hotspot-city-label');

  if (cityKey === 'all_india') {
    heading.innerText = "Whole India Transit";
    subtext.innerText = "Book Cabs, Autos & Skyways across any Indian State";
    netTag.innerHTML = `<span class="live-dot"></span> All-India Hubs Active`;
    chipLabel.innerText = "National Landmarks";
    mapMgr.viewWholeIndia();
  } else {
    heading.innerText = `Book Ride in ${city.name.split(' ')[0]}`;
    subtext.innerText = `Instant Ola Autos, Uber Cabs & DGCA Sky-Cabs in ${city.name}`;
    netTag.innerHTML = `<span class="live-dot"></span> ${city.tag}`;
    chipLabel.innerText = `${city.name.split(' ')[0]} Hubs`;
    mapMgr.centerCity(cityKey);
  }

  // Populate Hotspots
  renderHotspotChips(city.hotspots);

  // Set default pickup & drop from the first two hotspots
  if (city.hotspots.length >= 2) {
    state.pickup = {
      name: city.hotspots[0].name,
      lat: city.hotspots[0].lat,
      lng: city.hotspots[0].lng
    };
    state.drop = {
      name: city.hotspots[1].name,
      lat: city.hotspots[1].lat,
      lng: city.hotspots[1].lng
    };
    document.getElementById('pickup-input').value = state.pickup.name;
    document.getElementById('drop-input').value = state.drop.name;
    mapMgr.updatePickupDropMarkers();
    fetchFareEstimate();
  }

  // Refresh fleet radar for this city
  fetchNearbyDrivers();
}

function renderHotspotChips(hotspots) {
  const container = document.getElementById('hotspot-chips');
  container.innerHTML = '';
  hotspots.forEach((h, idx) => {
    const chip = document.createElement('button');
    chip.className = 'chip';
    chip.innerHTML = `${idx === 0 ? '🛫' : (idx === 1 ? '🏙️' : '📍')} ${h.name.split(',')[0].substring(0, 24)}`;
    chip.addEventListener('click', () => {
      sound.play('click');
      // Set as destination
      state.drop = { name: h.name, lat: h.lat, lng: h.lng };
      document.getElementById('drop-input').value = h.name;
      mapMgr.updatePickupDropMarkers();
      fetchFareEstimate();
      showToast(`🎯 Destination set to ${h.name.split(',')[0]}`, "info");
    });
    container.appendChild(chip);
  });
}

// ==========================================================================
// 6. Fare Estimator & Tier Selection
// ==========================================================================
async function fetchFareEstimate() {
  const p = state.pickup;
  const d = state.drop;
  try {
    const res = await fetch(`/api/rides/estimate?origin_lat=${p.lat}&origin_lng=${p.lng}&dest_lat=${d.lat}&dest_lng=${d.lng}`);
    if (res.ok) {
      const data = await res.json();
      state.estimates = data;
      updateTiersUI(data);
    }
  } catch (e) {
    console.error("Fare estimate failed:", e);
  }
}

function updateTiersUI(estimateData) {
  const dist = estimateData.distance_km;
  const distBadge = document.getElementById('route-dist-badge');
  if (distBadge) distBadge.innerText = `${dist} km`;
  const distHint = document.getElementById('tier-dist-hint');
  if (distHint) distHint.innerText = `${dist} km • Live Fare Comparison`;

  const container = document.getElementById('tiers-container');
  if (container && estimateData.options && estimateData.options.length > 0) {
    container.innerHTML = '';
    estimateData.options.forEach(opt => {
      const isSelected = opt.tier_id === state.selectedTier;
      const card = document.createElement('div');
      card.className = `tier-card ${isSelected ? 'active' : ''}`;
      card.dataset.tier = opt.tier_id;
      card.id = `tier-${opt.tier_id}`;

      let badgeHtml = '';
      if (opt.tier_id === 'auto') badgeHtml = '<div class="tier-badge budget-badge">MOST ECONOMICAL</div>';
      else if (opt.tier_id === 'standard') badgeHtml = '<div class="tier-badge popular-badge">MOST POPULAR</div>';
      else if (opt.tier_id === 'flying') badgeHtml = '<div class="tier-badge sky-badge">AIR TRANSIT • ZERO TRAFFIC</div>';
      else if (opt.tier_id === 'bike') badgeHtml = '<div class="tier-badge fast-badge">FASTEST GROUND</div>';

      const carImg = opt.car_image || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500';
      const driverPhoto = opt.driver_photo || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200';
      const driverName = opt.driver_name || 'Rajesh Kumar';
      const driverRating = opt.driver_rating || 4.92;
      const carModel = opt.car_model || opt.name;
      const plate = opt.license_plate || 'KA-05-EV-4242';

      card.innerHTML = `
        ${badgeHtml}
        <div class="tier-visual-block">
          <img src="${carImg}" alt="${carModel}" class="car-thumb-img" onerror="this.src='https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500'">
        </div>
        <div class="tier-info">
          <div class="tier-name-row">
            <span class="tier-name">${opt.icon} ${opt.name}</span>
            <span class="tier-price" id="price-${opt.tier_id}">₹${Math.round(opt.fare).toLocaleString('en-IN')}</span>
          </div>
          <div class="tier-car-model">${carModel} • <span class="plate-text">${plate}</span></div>
          <div class="pilot-face-chip" title="Assigned verified pilot for your ride">
            <img src="${driverPhoto}" alt="${driverName}" class="pilot-face-thumb" onerror="this.src='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200'">
            <span class="pilot-chip-name">${driverName}</span>
            <span class="pilot-chip-rating">★ ${driverRating}</span>
          </div>
          <div class="tier-meta">
            <span class="meta-tag">⚡ ${opt.eta_mins || 3} min away</span>
            <span class="meta-tag">👥 ${opt.capacity} Seats</span>
            <span class="meta-tag">⏱️ ${opt.duration_mins} min trip</span>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        sound.play('click');
        document.querySelectorAll('.tier-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        state.selectedTier = opt.tier_id;
        updateRequestButtonLabel();
        mapMgr.updatePickupDropMarkers();
      });

      container.appendChild(card);
    });
  }

  updateRequestButtonLabel();
  renderFleetShowcase(estimateData);
}

function renderFleetShowcase(estimateData) {
  const showcaseGrid = document.getElementById('fleet-showcase-grid');
  if (!showcaseGrid || !estimateData || !estimateData.options) return;
  showcaseGrid.innerHTML = '';

  estimateData.options.forEach(opt => {
    const card = document.createElement('div');
    card.className = 'showcase-vehicle-card';
    const carImg = opt.car_image || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500';
    const driverPhoto = opt.driver_photo || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200';
    const driverName = opt.driver_name || 'Rajesh Kumar';
    const driverRating = opt.driver_rating || 4.92;
    const carModel = opt.car_model || opt.name;
    const plate = opt.license_plate || 'KA-05-EV-4242';

    let specs = '';
    if (opt.tier_id === 'flying') {
      specs = `
        <span class="spec-badge">⚡ 320 km Range</span>
        <span class="spec-badge">🚀 160 km/h Sky Speed</span>
        <span class="spec-badge">🛸 150m Altitude</span>
        <span class="spec-badge">🛡️ DGCA Air Certified</span>
      `;
    } else if (opt.tier_id === 'luxury') {
      specs = `
        <span class="spec-badge">⚡ 450 km EV Range</span>
        <span class="spec-badge">🧳 3 Suitcases</span>
        <span class="spec-badge">✨ 5-Star Chauffeur</span>
        <span class="spec-badge">🍾 Executive Wi-Fi</span>
      `;
    } else if (opt.tier_id === 'auto') {
      specs = `
        <span class="spec-badge">⚡ Green Electric</span>
        <span class="spec-badge">👥 3 Passengers</span>
        <span class="spec-badge">🛺 Traffic Master</span>
      `;
    } else if (opt.tier_id === 'bike') {
      specs = `
        <span class="spec-badge">⚡ Ather Fast Charge</span>
        <span class="spec-badge">🪖 Sanitized Helmet</span>
        <span class="spec-badge">⚡ Fastest Commute</span>
      `;
    } else {
      specs = `
        <span class="spec-badge">❄️ AC Sedan</span>
        <span class="spec-badge">👥 4 Seats</span>
        <span class="spec-badge">🧳 2 Large Bags</span>
      `;
    }

    card.innerHTML = `
      <div class="showcase-img-wrap">
        <img src="${carImg}" alt="${carModel}" class="showcase-car-photo" onerror="this.src='https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500'">
        <span class="showcase-tier-badge">${opt.icon} ${opt.name}</span>
        <span class="showcase-fare-tag">₹${Math.round(opt.fare).toLocaleString('en-IN')}</span>
      </div>
      <div class="showcase-card-body">
        <div class="showcase-car-name">${carModel}</div>
        <div class="showcase-car-desc">${opt.description}</div>
        <div class="showcase-pilot-block">
          <img src="${driverPhoto}" alt="${driverName}" class="showcase-pilot-photo" onerror="this.src='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200'">
          <div class="showcase-pilot-details">
            <span class="showcase-pilot-name">${driverName}</span>
            <span class="showcase-pilot-meta">★ ${driverRating} Rating • Reg: ${plate}</span>
          </div>
        </div>
        <div class="showcase-specs-list">${specs}</div>
        <button class="btn-select-showcase-car" data-tier="${opt.tier_id}">
          Select ${carModel.split('/')[0]} • ₹${Math.round(opt.fare).toLocaleString('en-IN')}
        </button>
      </div>
    `;

    const selectBtn = card.querySelector('.btn-select-showcase-car');
    if (selectBtn) {
      selectBtn.addEventListener('click', () => {
        sound.play('click');
        state.selectedTier = opt.tier_id;
        document.querySelectorAll('.tier-card').forEach(c => {
          c.classList.toggle('active', c.dataset.tier === opt.tier_id);
        });
        updateRequestButtonLabel();
        document.getElementById('fleet-showcase-modal').classList.add('hidden');
        showToast(`Selected ${carModel} with pilot ${driverName}`, "success");
      });
    }

    showcaseGrid.appendChild(card);
  });
}

function updateRequestButtonLabel() {
  if (!state.estimates) return;
  const selectedOpt = state.estimates.options.find(o => o.tier_id === state.selectedTier);
  if (!selectedOpt) return;

  const payModeText = state.paymentMode === 'cash' ? ' (Cash to Driver)' : '';
  const labelEl = document.getElementById('request-btn-label');
  labelEl.innerText = `Book ${selectedOpt.name} • ₹${Math.round(selectedOpt.fare).toLocaleString('en-IN')}${payModeText}`;
}

// ==========================================================================
// 7. Booking & 4-Digit Ride Start OTP Lifecycle
// ==========================================================================
async function handleRequestRide() {
  sound.play('click');
  if (!state.estimates) return;

  const selectedOpt = state.estimates.options.find(o => o.tier_id === state.selectedTier);
  const payload = {
    rider_id: state.user.id,
    pickup_name: state.pickup.name,
    pickup_lat: state.pickup.lat,
    pickup_lng: state.pickup.lng,
    drop_name: state.drop.name,
    drop_lat: state.drop.lat,
    drop_lng: state.drop.lng,
    vehicle_type: state.selectedTier,
    fare_estimate: selectedOpt.fare,
    distance_km: selectedOpt.distance_km,
    duration_mins: selectedOpt.duration_mins,
    payment_mode: state.paymentMode
  };

  try {
    const res = await fetch(`/api/rides/request?auto_simulate=${state.autoSimulate}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const ride = await res.json();
      state.activeRide = ride;
      state.currentRideOtp = ride.otp || "4829";

      setRideStatusUI('REQUESTED');
      displayOtp(state.currentRideOtp);
      showToast(`⚡ Ride Requested! Searching for nearby cabs in ${state.currentCity}...`, "success");

      // Notify Driver Cockpit if in simulation/cockpit view
      triggerDriverIncomingAlert(ride, selectedOpt);
    }
  } catch (e) {
    console.error("Booking error:", e);
    showToast("Booking failed. Please retry.", "alert");
  }
}

function displayOtp(otpString) {
  const digits = String(otpString).padStart(4, '0').split('');
  document.getElementById('otp-d1').innerText = digits[0] || '4';
  document.getElementById('otp-d2').innerText = digits[1] || '8';
  document.getElementById('otp-d3').innerText = digits[2] || '2';
  document.getElementById('otp-d4').innerText = digits[3] || '9';
}

function setRideStatusUI(status) {
  const card = document.getElementById('active-ride-card');
  const badgeText = document.getElementById('ride-status-text');
  const radarWrap = document.getElementById('searching-radar-wrap');
  const driverWidget = document.getElementById('driver-profile-widget');
  const otpBox = document.getElementById('otp-security-box');
  const contactActions = document.getElementById('driver-contact-actions');
  const fill = document.getElementById('ride-progress-fill');
  const etaMsg = document.getElementById('eta-message');
  const completeActions = document.getElementById('ride-complete-actions');

  card.classList.remove('hidden');

  // Reset steps
  ['step-requested', 'step-accepted', 'step-arrived', 'step-transit', 'step-completed'].forEach(id => {
    document.getElementById(id).classList.remove('active');
  });

  if (status === 'REQUESTED') {
    badgeText.innerText = "SEARCHING FOR NEARBY DRIVERS...";
    radarWrap.classList.remove('hidden');
    driverWidget.classList.add('hidden');
    otpBox.classList.add('hidden');
    contactActions.classList.add('hidden');
    completeActions.classList.add('hidden');
    fill.style.width = '10%';
    document.getElementById('step-requested').classList.add('active');
    etaMsg.innerText = "Broadcasting dispatch to active drivers in your sector...";
  } else if (status === 'ACCEPTED') {
    sound.play('accept');
    badgeText.innerText = "DRIVER CONFIRMED & EN ROUTE";
    radarWrap.classList.add('hidden');
    driverWidget.classList.remove('hidden');
    otpBox.classList.remove('hidden');
    contactActions.classList.remove('hidden');
    completeActions.classList.add('hidden');
    fill.style.width = '35%';
    document.getElementById('step-requested').classList.add('active');
    document.getElementById('step-accepted').classList.add('active');
    etaMsg.innerText = "Driver is on the way to your pickup point. Share OTP upon arrival.";
  } else if (status === 'ARRIVED') {
    sound.play('arrived');
    badgeText.innerText = "CAB ARRIVED AT PICKUP";
    radarWrap.classList.add('hidden');
    driverWidget.classList.remove('hidden');
    otpBox.classList.remove('hidden');
    fill.style.width = '55%';
    document.getElementById('step-arrived').classList.add('active');
    etaMsg.innerText = `Cab has arrived! Share 4-digit OTP (${state.currentRideOtp}) to begin trip.`;
  } else if (status === 'IN_PROGRESS') {
    sound.play('otp_verified');
    badgeText.innerText = "TRIP IN PROGRESS";
    radarWrap.classList.add('hidden');
    driverWidget.classList.remove('hidden');
    otpBox.classList.add('hidden'); // OTP verified, no longer needed
    fill.style.width = '80%';
    document.getElementById('step-transit').classList.add('active');
    etaMsg.innerText = "Cruising smoothly towards your destination.";
  } else if (status === 'COMPLETED') {
    sound.play('complete');
    badgeText.innerText = "ARRIVED AT DESTINATION";
    radarWrap.classList.add('hidden');
    driverWidget.classList.remove('hidden');
    otpBox.classList.add('hidden');
    completeActions.classList.remove('hidden');
    fill.style.width = '100%';
    document.getElementById('step-completed').classList.add('active');
    etaMsg.innerText = "You have safely arrived! Please complete payment & rate your driver.";
  }
}

// ==========================================================================
// 8. Driver Cockpit Mode & OTP Verification
// ==========================================================================
function triggerDriverIncomingAlert(ride, tierOpt) {
  const incCard = document.getElementById('driver-incoming-card');
  if (!incCard) return;

  incCard.classList.remove('hidden');
  document.getElementById('incoming-fare').innerText = `₹${Math.round(ride.fare_estimate).toLocaleString('en-IN')}`;
  document.getElementById('incoming-pickup').innerText = ride.pickup_name;
  document.getElementById('incoming-drop').innerText = ride.drop_name;
  document.getElementById('incoming-dist').innerText = `${ride.distance_km} km`;
  document.getElementById('incoming-tier').innerText = tierOpt ? tierOpt.name : ride.vehicle_type;

  sound.play('dispatch');

  let seconds = 15;
  const timerEl = document.getElementById('dispatch-timer-sec');
  if (state.dispatchTimerInterval) clearInterval(state.dispatchTimerInterval);
  state.dispatchTimerInterval = setInterval(() => {
    seconds--;
    if (timerEl) timerEl.innerText = seconds;
    if (seconds <= 0) {
      clearInterval(state.dispatchTimerInterval);
      incCard.classList.add('hidden');
    }
  }, 1000);
}

async function handleDriverAccept() {
  sound.play('accept');
  if (state.dispatchTimerInterval) clearInterval(state.dispatchTimerInterval);
  document.getElementById('driver-incoming-card').classList.add('hidden');

  if (!state.activeRide) return;

  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/accept?driver_id=${state.activeDriver.id}`, {
      method: 'POST'
    });
    if (res.ok) {
      const ride = await res.json();
      state.activeRide = ride;
      setRideStatusUI('ACCEPTED');

      const ctrlCard = document.getElementById('driver-controls-card');
      ctrlCard.classList.remove('hidden');
      document.getElementById('driver-control-status').innerText = "En route to passenger pickup point.";
      document.getElementById('btn-driver-step-arrived').disabled = false;
      document.getElementById('btn-driver-step-arrived').classList.remove('disabled');

      showToast("✅ Dispatch accepted! Driving to passenger pickup.", "success");
    }
  } catch (e) {
    console.error("Accept failed:", e);
  }
}

async function handleDriverArrivedAtPickup() {
  sound.play('arrived');
  if (!state.activeRide) return;

  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: "ARRIVED" })
    });
    if (res.ok) {
      setRideStatusUI('ARRIVED');
      document.getElementById('driver-control-status').innerText = "Arrived at pickup. Ask passenger for 4-digit OTP to start trip.";
      document.getElementById('btn-driver-step-arrived').disabled = true;
      document.getElementById('btn-driver-step-arrived').classList.add('disabled');
      document.getElementById('driver-otp-input').focus();
      showToast("📍 Marked Arrived! Enter passenger OTP to start trip.", "info");
    }
  } catch (e) {
    console.error("Arrived update error:", e);
  }
}

async function handleVerifyDriverOtp() {
  sound.play('click');
  const inputEl = document.getElementById('driver-otp-input');
  const enteredOtp = inputEl.value.trim();

  if (!enteredOtp || enteredOtp.length !== 4) {
    showToast("⚠️ Please enter a 4-digit OTP", "alert");
    return;
  }

  if (enteredOtp !== state.currentRideOtp) {
    showToast(`❌ Invalid OTP. Passenger OTP is ${state.currentRideOtp}`, "alert");
    return;
  }

  // OTP Match: Start Ride
  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: "IN_PROGRESS", entered_otp: enteredOtp })
    });

    if (res.ok) {
      sound.play('otp_verified');
      setRideStatusUI('IN_PROGRESS');
      document.getElementById('driver-control-status').innerText = "Trip Started! Navigating to drop destination.";
      document.getElementById('btn-driver-step-start').disabled = true;
      document.getElementById('btn-driver-step-start').classList.add('disabled');
      document.getElementById('btn-driver-step-complete').disabled = false;
      document.getElementById('btn-driver-step-complete').classList.remove('disabled');
      document.getElementById('driver-otp-verify-section').classList.add('hidden');
      showToast("🛡️ OTP Verified! Trip in progress.", "success");
    }
  } catch (e) {
    console.error("Trip start failed:", e);
  }
}

async function handleDriverCompleteTrip() {
  sound.play('complete');
  if (!state.activeRide) return;

  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: "COMPLETED" })
    });
    if (res.ok) {
      setRideStatusUI('COMPLETED');
      document.getElementById('driver-controls-card').classList.add('hidden');
      showToast("🏁 Trip completed! Shift earnings updated.", "success");
      loadDriverMetrics();
    }
  } catch (e) {
    console.error("Complete trip error:", e);
  }
}

async function loadDriverMetrics() {
  try {
    const res = await fetch(`/api/drivers/${state.activeDriver.id}/dashboard`);
    if (res.ok) {
      const data = await res.json();
      document.getElementById('metric-earnings').innerText = `₹${Math.round(data.driver.earnings_today).toLocaleString('en-IN')}`;
      document.getElementById('metric-trips').innerText = data.driver.total_trips;
      document.getElementById('metric-rating').innerText = `${data.driver.rating_avg} ★`;
      document.getElementById('metric-battery').innerText = `${data.driver.battery_pct}% ⚡`;
    }
  } catch (e) {
    console.error("Metrics load error:", e);
  }
}

// ==========================================================================
// 9. Razorpay Payment Gateway & Cash Integration
// ==========================================================================
function updatePayButtonText() {
  const activeMethodEl = document.querySelector('.payment-method-selector .method-option.active');
  const selectedMethod = activeMethodEl ? activeMethodEl.dataset.method : "Razorpay (UPI / Cards / NetBanking)";
  const tipChip = document.querySelector('.tip-chip.active');
  const tipAmount = tipChip ? parseFloat(tipChip.dataset.tip) : 0;
  const baseFare = state.activeRide ? (state.activeRide.fare_actual || state.activeRide.fare_estimate || 580) : 580;
  const total = baseFare + tipAmount;
  const payBtn = document.getElementById('btn-confirm-payment');
  if (!payBtn) return;

  if (selectedMethod.includes("Cash")) {
    payBtn.innerHTML = `<span>Confirm Cash Payment to Driver</span><span id="btn-pay-total">₹${Math.round(total).toLocaleString('en-IN')}</span>`;
  } else if (selectedMethod.includes("Wallet") || selectedMethod.includes("Ola Money")) {
    payBtn.innerHTML = `<span>Pay from Ola Money Wallet</span><span id="btn-pay-total">₹${Math.round(total).toLocaleString('en-IN')}</span>`;
  } else if (selectedMethod.includes("UPI Direct QR")) {
    payBtn.innerHTML = `<span>Open Bharat UPI Dynamic QR</span><span id="btn-pay-total">₹${Math.round(total).toLocaleString('en-IN')}</span>`;
  } else {
    payBtn.innerHTML = `<span>Authorize & Pay with Razorpay</span><span id="btn-pay-total">₹${Math.round(total).toLocaleString('en-IN')}</span>`;
  }
}

let rzpCountdownInterval = null;

function generateRazorpaySvgQr(payloadText) {
  // Deterministic SVG QR Matrix (25x25) with authentic position detection patterns
  const size = 25;
  const matrix = Array.from({ length: size }, () => Array(size).fill(false));

  function drawFinder(r0, c0) {
    for (let r = 0; r < 7; r++) {
      for (let c = 0; c < 7; c++) {
        if (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)) {
          matrix[r0 + r][c0 + c] = true;
        }
      }
    }
  }

  drawFinder(0, 0);
  drawFinder(0, size - 7);
  drawFinder(size - 7, 0);

  for (let i = 8; i < size - 8; i++) {
    if (i % 2 === 0) {
      matrix[6][i] = true;
      matrix[i][6] = true;
    }
  }

  let hash = 0;
  for (let i = 0; i < payloadText.length; i++) {
    hash = (hash << 5) - hash + payloadText.charCodeAt(i);
    hash |= 0;
  }

  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if ((r < 8 && c < 8) || (r < 8 && c >= size - 8) || (r >= size - 8 && c < 8) || r === 6 || c === 6) continue;
      const seed = Math.sin((r * size + c + hash) * 12.9898) * 43758.5453;
      if (seed - Math.floor(seed) > 0.45) {
        matrix[r][c] = true;
      }
    }
  }

  let rects = '';
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (matrix[r][c]) {
        rects += `<rect x="${c}" y="${r}" width="1" height="1" fill="#0c1424"/>`;
      }
    }
  }

  return `<svg viewBox="0 0 ${size} ${size}" shape-rendering="crispEdges" style="width:100%; height:100%;">${rects}</svg>`;
}

function openRazorpaySandboxGateway(orderData, totalAmount, activeRide, defaultTab = "upi") {
  sound.play('dispatch');
  const modal = document.getElementById('razorpay-sandbox-modal');
  if (!modal) return;

  const merchantEl = document.getElementById('rzp-merchant-name');
  if (merchantEl) merchantEl.innerText = state.apiConfig.merchant_name || "Flying Cabs (Ola-Uber Bharat)";

  const orderRefEl = document.getElementById('rzp-order-ref');
  if (orderRefEl) orderRefEl.innerText = `Order: ${orderData.order_id || 'order_mock_' + (activeRide ? activeRide.id : '1')}`;

  const amountEl = document.getElementById('rzp-modal-amount');
  if (amountEl) amountEl.innerText = `₹${Math.round(totalAmount).toLocaleString('en-IN')}`;

  document.querySelectorAll('.rzp-btn-amount').forEach(el => {
    el.innerText = Math.round(totalAmount).toLocaleString('en-IN');
  });

  const badgeEl = document.getElementById('rzp-modal-badge');
  if (badgeEl) {
    badgeEl.innerText = orderData.is_live ? "Razorpay Live Mode" : "Razorpay Sandbox / Test";
  }

  const qrContainer = document.getElementById('rzp-qr-svg-container');
  if (qrContainer) {
    const upiPayload = `upi://pay?pa=flyingcabs.rzp@icici&pn=FlyingCabs&am=${totalAmount}&tr=${orderData.order_id}&cu=INR`;
    qrContainer.innerHTML = generateRazorpaySvgQr(upiPayload);
  }

  let remainingSeconds = 299;
  const countdownEl = document.getElementById('rzp-qr-countdown');
  if (rzpCountdownInterval) clearInterval(rzpCountdownInterval);
  rzpCountdownInterval = setInterval(() => {
    remainingSeconds--;
    if (remainingSeconds < 0) {
      clearInterval(rzpCountdownInterval);
      if (countdownEl) countdownEl.innerText = "Expired";
      return;
    }
    const mins = String(Math.floor(remainingSeconds / 60)).padStart(2, '0');
    const secs = String(remainingSeconds % 60).padStart(2, '0');
    if (countdownEl) countdownEl.innerText = `${mins}:${secs}`;
  }, 1000);

  const otpScreen = document.getElementById('rzp-card-otp-screen');
  const cardForm = document.getElementById('rzp-card-form-wrap');
  if (otpScreen) otpScreen.classList.add('hidden');
  if (cardForm) cardForm.classList.remove('hidden');

  switchRazorpayTab(defaultTab);
  modal.classList.remove('hidden');
}

function switchRazorpayTab(tabName) {
  document.querySelectorAll('.rzp-nav-item').forEach(btn => {
    if (btn.dataset.tab === tabName) btn.classList.add('active');
    else btn.classList.remove('active');
  });

  document.querySelectorAll('.rzp-pane').forEach(pane => {
    pane.classList.remove('active');
  });

  const activePane = document.getElementById(`rzp-pane-${tabName}`);
  if (activePane) activePane.classList.add('active');
}

async function executeRazorpayVerification(methodName, customOrderId, customPayId, signature) {
  if (!state.activeRide) {
    showToast("No active ride found to verify", "alert");
    return;
  }

  sound.play('click');
  const overlay = document.getElementById('rzp-processing-overlay');
  const title = document.getElementById('rzp-proc-title');
  const desc = document.getElementById('rzp-proc-desc');
  if (overlay) {
    title.innerText = "Securing transaction with Bank / NPCI...";
    desc.innerText = "Encrypting with Razorpay 256-Bit SSL certificate...";
    overlay.classList.remove('hidden');
  }

  const tipChip = document.querySelector('.tip-chip.active');
  const tipAmount = tipChip ? parseFloat(tipChip.dataset.tip) : 0;
  const baseFare = state.activeRide.fare_actual || state.activeRide.fare_estimate || 580;
  const total = baseFare + tipAmount;

  const currentOrderId = customOrderId || `order_mock_${Math.random().toString(36).substring(2, 12)}`;
  const txnId = customPayId || `pay_rzp_${Math.random().toString(36).substring(2, 12)}`;
  const sig = signature || `mock_sig_${Math.random().toString(36).substring(2, 16)}`;

  setTimeout(async () => {
    try {
      if (title) title.innerText = "Payment Authorized! Verifying...";
      const verifyRes = await fetch(`/api/rides/${state.activeRide.id}/razorpay/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          razorpay_order_id: currentOrderId,
          razorpay_payment_id: txnId,
          razorpay_signature: sig,
          amount: total,
          payment_method: methodName || "Razorpay (UPI / Card)"
        })
      });

      if (verifyRes.ok) {
        sound.play('complete');
        if (overlay) overlay.classList.add('hidden');
        document.getElementById('payment-modal').classList.add('hidden');
        const rzpModal = document.getElementById('razorpay-sandbox-modal');
        if (rzpModal) rzpModal.classList.add('hidden');
        showToast(`🛡️ Razorpay Payment Verified! ID: ${txnId}`, "success");
        document.getElementById('review-modal').classList.remove('hidden');
      } else {
        throw new Error("Verification failed");
      }
    } catch (e) {
      if (overlay) overlay.classList.add('hidden');
      showToast(`🛡️ Payment Authorized! ID: ${txnId}`, "success");
      document.getElementById('payment-modal').classList.add('hidden');
      const rzpModal = document.getElementById('razorpay-sandbox-modal');
      if (rzpModal) rzpModal.classList.add('hidden');
      document.getElementById('review-modal').classList.remove('hidden');
    }
  }, 1100);
}

function initRazorpaySandboxListeners() {
  document.querySelectorAll('.rzp-nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      sound.play('click');
      switchRazorpayTab(btn.dataset.tab);
    });
  });

  const closeBtn = document.getElementById('btn-close-rzp-modal');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      document.getElementById('razorpay-sandbox-modal').classList.add('hidden');
      if (rzpCountdownInterval) clearInterval(rzpCountdownInterval);
    });
  }

  document.querySelectorAll('.rzp-upi-apps-grid .rzp-app-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const app = btn.dataset.app || "UPI App";
      executeRazorpayVerification(`Razorpay (UPI - ${app})`);
    });
  });

  const vpaBtn = document.getElementById('btn-rzp-pay-vpa');
  if (vpaBtn) {
    vpaBtn.addEventListener('click', () => {
      const vpaInput = document.getElementById('rzp-vpa-input');
      const vpa = vpaInput ? vpaInput.value.trim() : "aarav@okaxis";
      executeRazorpayVerification(`Razorpay (UPI VPA: ${vpa})`);
    });
  }

  const scanBtn = document.getElementById('btn-rzp-scan-sim');
  if (scanBtn) {
    scanBtn.addEventListener('click', () => {
      executeRazorpayVerification("Razorpay (Bharat UPI Dynamic QR)");
    });
  }

  const fillCardBtn = document.getElementById('btn-rzp-fill-card');
  if (fillCardBtn) {
    fillCardBtn.addEventListener('click', () => {
      sound.play('click');
      document.getElementById('rzp-card-number').value = "4111 2222 3333 4444";
      document.getElementById('rzp-card-expiry').value = "12/28";
      document.getElementById('rzp-card-cvv').value = "123";
      document.getElementById('rzp-card-name').value = state.user?.name || "Aarav Sharma";
      showToast("💳 Test card filled (RuPay/Visa Sandbox)", "info");
    });
  }

  const payCardBtn = document.getElementById('btn-rzp-pay-card');
  if (payCardBtn) {
    payCardBtn.addEventListener('click', () => {
      sound.play('click');
      document.getElementById('rzp-card-form-wrap').classList.add('hidden');
      const otpScreen = document.getElementById('rzp-card-otp-screen');
      if (otpScreen) {
        otpScreen.classList.remove('hidden');
        const otpInp = document.getElementById('rzp-bank-otp');
        if (otpInp) otpInp.focus();
      }
    });
  }

  const submitOtpBtn = document.getElementById('btn-rzp-submit-otp');
  if (submitOtpBtn) {
    submitOtpBtn.addEventListener('click', () => {
      const otpVal = document.getElementById('rzp-bank-otp').value || "123456";
      executeRazorpayVerification(`Razorpay (RuPay/Visa Card - 3DS OTP: ${otpVal})`);
    });
  }

  document.querySelectorAll('.rzp-banks-grid .rzp-bank-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sound.play('click');
      document.querySelectorAll('.rzp-banks-grid .rzp-bank-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const bankName = btn.dataset.bank;
      const labelEl = document.getElementById('rzp-selected-bank-name');
      if (labelEl) labelEl.innerText = bankName;
    });
  });

  const payBankBtn = document.getElementById('btn-rzp-pay-bank');
  if (payBankBtn) {
    payBankBtn.addEventListener('click', () => {
      const activeBank = document.querySelector('.rzp-banks-grid .rzp-bank-btn.active');
      const bankName = activeBank ? activeBank.dataset.bank : "State Bank of India";
      executeRazorpayVerification(`Razorpay (NetBanking - ${bankName})`);
    });
  }

  document.querySelectorAll('.rzp-wallets-list .rzp-wallet-item').forEach(item => {
    item.addEventListener('click', () => {
      sound.play('click');
      document.querySelectorAll('.rzp-wallets-list .rzp-wallet-item').forEach(i => {
        i.classList.remove('active');
        i.querySelector('.wallet-check').innerText = '';
      });
      item.classList.add('active');
      item.querySelector('.wallet-check').innerText = '✓';
    });
  });

  const payWalletBtn = document.getElementById('btn-rzp-pay-wallet');
  if (payWalletBtn) {
    payWalletBtn.addEventListener('click', () => {
      const activeWallet = document.querySelector('.rzp-wallets-list .rzp-wallet-item.active');
      const walletName = activeWallet ? activeWallet.dataset.wallet : "Ola Money / Cab Wallet";
      executeRazorpayVerification(`Razorpay (Wallet - ${walletName})`);
    });
  }
}

async function handleConfirmPayment() {
  sound.play('click');
  if (!state.activeRide) {
    showToast("No active ride found to pay for", "alert");
    return;
  }

  const activeMethodEl = document.querySelector('.payment-method-selector .method-option.active');
  const selectedMethod = activeMethodEl ? activeMethodEl.dataset.method : "Razorpay (UPI / Cards / NetBanking)";

  const tipChip = document.querySelector('.tip-chip.active');
  const tipAmount = tipChip ? parseFloat(tipChip.dataset.tip) : 0;
  const baseFare = state.activeRide.fare_actual || state.activeRide.fare_estimate || 580;
  const total = baseFare + tipAmount;

  // 1. CASH TO DRIVER (Ola / Uber Classic)
  if (selectedMethod.includes("Cash")) {
    try {
      const res = await fetch(`/api/rides/${state.activeRide.id}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: total, payment_method: "Cash to Driver" })
      });
      if (res.ok) {
        sound.play('complete');
        document.getElementById('payment-modal').classList.add('hidden');
        showToast(`💵 ₹${Math.round(total).toLocaleString('en-IN')} Cash Paid to Driver!`, "success");
        document.getElementById('review-modal').classList.remove('hidden');
      }
    } catch (e) {
      showToast("Payment confirmation failed", "alert");
    }
    return;
  }

  // 2. OLA MONEY / CAB WALLET
  if (selectedMethod.includes("Wallet") || selectedMethod.includes("Ola Money")) {
    try {
      const res = await fetch(`/api/rides/${state.activeRide.id}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: total, payment_method: "Ola Money / Cab Wallet" })
      });
      if (res.ok) {
        sound.play('complete');
        document.getElementById('payment-modal').classList.add('hidden');
        showToast(`🪙 ₹${Math.round(total).toLocaleString('en-IN')} debited from Ola Money Wallet!`, "success");
        document.getElementById('review-modal').classList.remove('hidden');
      }
    } catch (e) {
      showToast("Wallet payment failed", "alert");
    }
    return;
  }

  // 3. RAZORPAY GATEWAY (UPI, Cards, NetBanking, Bharat QR)
  const payBtn = document.getElementById('btn-confirm-payment');
  payBtn.disabled = true;
  payBtn.innerHTML = '<span>Opening Razorpay Gateway...</span>';

  try {
    const orderRes = await fetch(`/api/rides/${state.activeRide.id}/razorpay/create-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: baseFare, tip: tipAmount })
    });

    if (!orderRes.ok) throw new Error("Order creation failed");
    const orderData = await orderRes.json();

    // If live credentials are valid on Razorpay and SDK is loaded:
    if (orderData.is_live && typeof window.Razorpay === 'function') {
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: state.apiConfig.merchant_name || "Flying Cabs (Ola-Uber Bharat)",
        description: `Booking #${state.activeRide.id} • ${state.activeRide.pickup_name} to ${state.activeRide.drop_name}`,
        image: "/static/assets/logo.png",
        order_id: orderData.order_id,
        handler: async function (rzpResponse) {
          const verifyRes = await fetch(`/api/rides/${state.activeRide.id}/razorpay/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              razorpay_order_id: rzpResponse.razorpay_order_id || orderData.order_id,
              razorpay_payment_id: rzpResponse.razorpay_payment_id,
              razorpay_signature: rzpResponse.razorpay_signature || "mock_signature_test",
              amount: total,
              payment_method: "Razorpay (Official Gateway)"
            })
          });

          if (verifyRes.ok) {
            sound.play('complete');
            document.getElementById('payment-modal').classList.add('hidden');
            showToast(`🛡️ Razorpay Payment Verified! ID: ${rzpResponse.razorpay_payment_id}`, "success");
            document.getElementById('review-modal').classList.remove('hidden');
          }
        },
        prefill: {
          name: state.user?.name || "Passenger",
          email: state.user?.email || "passenger@aerocabs.in",
          contact: state.user?.phone || "+91 98765 43210"
        },
        theme: { color: "#0284c7" }
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', (err) => {
        showToast(`Official Razorpay note: ${err.error.description}. Opening Sandbox Gateway...`, "info");
        openRazorpaySandboxGateway(orderData, total, state.activeRide, selectedMethod.includes("UPI Direct QR") ? "upi" : "upi");
      });
      rzp.open();
    } else {
      // Launch Interactive Razorpay Sandbox Gateway
      openRazorpaySandboxGateway(orderData, total, state.activeRide, selectedMethod.includes("UPI Direct QR") ? "upi" : "upi");
    }
  } catch (err) {
    console.warn("Razorpay Order fallback to Sandbox Gateway:", err);
    openRazorpaySandboxGateway({
      order_id: `order_mock_${Math.random().toString(36).substring(2, 10)}`,
      amount: Math.round(total * 100),
      currency: "INR",
      key_id: state.apiConfig.razorpay_key_id
    }, total, state.activeRide, selectedMethod.includes("UPI Direct QR") ? "upi" : "upi");
  } finally {
    payBtn.disabled = false;
    updatePayButtonText();
  }
}

// ==========================================================================
// 10. API Keys Management Modal
// ==========================================================================
function updateConfigModalInputs() {
  const gKeyInput = document.getElementById('cfg-gmaps-key');
  const rKeyInput = document.getElementById('cfg-razorpay-key');
  const mTypeSelect = document.getElementById('cfg-gmaps-type');

  if (gKeyInput) gKeyInput.value = state.apiConfig.google_maps_api_key || "";
  if (rKeyInput) rKeyInput.value = state.apiConfig.razorpay_key_id || "";
  if (mTypeSelect) mTypeSelect.value = state.apiConfig.google_maps_map_type || "terrain";
}

async function handleSaveApiKeys() {
  sound.play('click');
  const gmapsKey = document.getElementById('cfg-gmaps-key').value.trim();
  const gmapsType = document.getElementById('cfg-gmaps-type').value;
  const rzpKey = document.getElementById('cfg-razorpay-key').value.trim();
  const rzpSecret = document.getElementById('cfg-razorpay-secret').value.trim();

  try {
    const res = await fetch('/api/rides/config/keys', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        google_maps_api_key: gmapsKey,
        google_maps_map_type: gmapsType,
        razorpay_key_id: rzpKey,
        razorpay_key_secret: rzpSecret || undefined
      })
    });

    if (res.ok) {
      state.apiConfig = await res.json();
      document.getElementById('api-keys-modal').classList.add('hidden');
      showToast("🔑 API Keys saved and applied successfully!", "success");

      // If user provided a live Google Maps API key, re-try loading
      if (gmapsKey && !gmapsKey.startsWith("AIzaSyDemo")) {
        mapMgr.tryLoadGoogleMaps();
      }
    }
  } catch (e) {
    showToast("Failed to save API keys", "alert");
  }
}

// ==========================================================================
// 11. Fleet Radar & Nearby Drivers
// ==========================================================================
async function fetchNearbyDrivers() {
  try {
    const city = CITIES_DATA[state.currentCity];
    const center = city.center;
    const radius = state.currentCity === 'all_india' ? 3000 : 40;

    const res = await fetch(`/api/drivers/nearby?lat=${center[0]}&lng=${center[1]}&radius_km=${radius}`);
    if (res.ok) {
      const drivers = await res.json();
      mapMgr.renderFleetMarkers(drivers);
      renderFleetList(drivers);
    }
  } catch (e) {
    console.error("Nearby drivers error:", e);
  }
}

function renderFleetList(drivers) {
  const listEl = document.getElementById('fleet-cabs-list');
  if (!listEl) return;
  listEl.innerHTML = '';

  let skyCount = 0;
  let groundCount = 0;

  drivers.forEach(d => {
    if (d.vehicle_type === 'flying') skyCount++;
    else groundCount++;

    const icon = d.vehicle_type === 'flying' ? '🛸' : (d.vehicle_type === 'auto' ? '🛺' : (d.vehicle_type === 'bike' ? '🏍️' : '🚖'));
    const item = document.createElement('div');
    item.className = 'fleet-cab-item';
    item.innerHTML = `
      <div class="cab-left">
        <span class="cab-icon">${icon}</span>
        <div>
          <div class="cab-model">${d.vehicle_info}</div>
          <div class="cab-status">● ${d.status.toUpperCase()} • ${d.license_plate}</div>
        </div>
      </div>
      <div class="cab-telemetry">
        <div>${d.altitude_m > 0 ? `${Math.round(d.altitude_m)}m Alt` : 'Ground'}</div>
        <div>${d.battery_pct}% Batt</div>
      </div>
    `;
    item.addEventListener('click', () => {
      sound.play('click');
      if (mapMgr.leafletMap) {
        mapMgr.leafletMap.flyTo([d.current_lat, d.current_lng], 15);
      }
    });
    listEl.appendChild(item);
  });

  document.getElementById('stat-total-cabs').innerText = drivers.length;
  document.getElementById('stat-in-flight').innerText = skyCount;
  document.getElementById('stat-ground-cabs').innerText = groundCount;
}

// ==========================================================================
// 12. WebSocket Real-Time Telemetry & Updates
// ==========================================================================
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/rider/${state.user.id}`;
  const socket = new WebSocket(wsUrl);

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      const evType = msg.type || msg.event || (msg.data && msg.data.event);
      if (evType === 'RIDE_ACCEPTED') {
        const d = msg.data.driver;
        state.activeDriver = d;
        if (msg.data.otp) {
          state.currentRideOtp = msg.data.otp;
          displayOtp(state.currentRideOtp);
        }
        document.getElementById('widget-driver-name').innerText = d.name;
        document.getElementById('widget-driver-rating').innerText = `★ ${d.rating_avg}`;
        document.getElementById('widget-vehicle-name').innerText = d.vehicle_info;
        document.getElementById('widget-plate').innerText = d.license_plate;
        const driverImgEl = document.getElementById('widget-driver-img');
        if (driverImgEl && (d.profile_pic || d.driver_photo)) {
          driverImgEl.src = d.profile_pic || d.driver_photo;
        }
        setRideStatusUI('ACCEPTED');
        mapMgr.updateDriverMarker(d.current_lat, d.current_lng, d.altitude_m, d.vehicle_type, d.license_plate);
      } else if (evType === 'DRIVER_LOCATION_UPDATE') {
        const loc = msg.data;
        mapMgr.updateDriverMarker(loc.lat, loc.lng, loc.altitude_m, state.selectedTier, "AERO");
        document.getElementById('widget-altitude').innerText = loc.altitude_m > 0 ? `Alt: ${Math.round(loc.altitude_m)}m` : 'Ground';
      } else if (evType === 'DRIVER_ARRIVED') {
        setRideStatusUI('ARRIVED');
        showToast("🚖 Your cab has arrived at the pickup platform!", "success");
      } else if (evType === 'RIDE_STARTED') {
        setRideStatusUI('IN_PROGRESS');
      } else if (evType === 'RIDE_COMPLETED') {
        setRideStatusUI('COMPLETED');
        if (state.activeRide && msg.data && msg.data.fare) {
          state.activeRide.fare_actual = msg.data.fare;
          state.activeRide.status = 'COMPLETED';
        }
        showToast("🏁 Trip completed! Please authorize payment & review your driver.", "success");
      } else if (evType === 'PAYMENT_CONFIRMED') {
        sound.play('complete');
        document.getElementById('payment-modal').classList.add('hidden');
        const rzpModal = document.getElementById('razorpay-sandbox-modal');
        if (rzpModal) rzpModal.classList.add('hidden');
        const amt = msg.data?.amount ? `₹${Math.round(msg.data.amount).toLocaleString('en-IN')}` : '';
        showToast(`💳 Payment Confirmed! ${amt}`, "success");
        document.getElementById('review-modal').classList.remove('hidden');
      }
    } catch (e) {
      console.warn("WS parse error:", e);
    }
  };

  socket.onclose = () => {
    setTimeout(initWebSocket, 4000);
  };
}

// ==========================================================================
// 13. Receipts, Reviews, and History
// ==========================================================================
async function openReceiptModal() {
  sound.play('click');
  if (!state.activeRide) return;

  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/receipt`);
    if (res.ok) {
      const rcp = await res.json();
      document.getElementById('rcp-number').innerText = rcp.receipt_number;
      const body = document.getElementById('receipt-content');
      body.innerHTML = `
        <div class="receipt-line-item"><span>TAX INVOICE</span><span>${rcp.receipt_number}</span></div>
        <div class="receipt-line-item"><span>DATE / TIME</span><span>${rcp.date}</span></div>
        <div class="receipt-line-item"><span>PASSENGER</span><span>${rcp.rider_name}</span></div>
        <div class="receipt-line-item"><span>DRIVER</span><span>${rcp.driver_name}</span></div>
        <div class="receipt-line-item"><span>VEHICLE</span><span>${rcp.vehicle} (${rcp.vehicle_type.toUpperCase()})</span></div>
        <div class="rcp-divider"></div>
        <div class="receipt-line-item"><span>PICKUP</span><span>${rcp.pickup}</span></div>
        <div class="receipt-line-item"><span>DROPOFF</span><span>${rcp.dropoff}</span></div>
        <div class="receipt-line-item"><span>DISTANCE</span><span>${rcp.distance_km} km</span></div>
        <div class="rcp-divider"></div>
        <div class="receipt-line-item"><span>Base Fare</span><span>₹${Math.round(rcp.breakdown.base_fare).toLocaleString('en-IN')}</span></div>
        <div class="receipt-line-item"><span>Distance Fare</span><span>₹${Math.round(rcp.breakdown.distance_charge).toLocaleString('en-IN')}</span></div>
        <div class="receipt-line-item"><span>GST (5% Indian Passenger Transport)</span><span>₹${rcp.breakdown.taxes_and_fees.toFixed(2)}</span></div>
        <div class="rcp-divider"></div>
        <div class="receipt-line-item rcp-total"><span>TOTAL CHARGED</span><span>₹${Math.round(rcp.breakdown.total).toLocaleString('en-IN')}</span></div>
        <div class="receipt-line-item"><span>PAYMENT METHOD</span><span>${rcp.payment.method} (${rcp.payment.status.toUpperCase()})</span></div>
      `;
      document.getElementById('receipt-modal').classList.remove('hidden');
    }
  } catch (e) {
    console.error("Receipt error:", e);
  }
}

async function handleSubmitReview() {
  sound.play('click');
  if (!state.activeRide) return;

  const stars = document.querySelectorAll('#star-rating-row .star.selected').length;
  const comment = document.getElementById('review-comment-input').value;

  try {
    const res = await fetch(`/api/rides/${state.activeRide.id}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: stars, comment: comment })
    });
    if (res.ok) {
      document.getElementById('review-modal').classList.add('hidden');
      showToast("⭐ Rating submitted! Thank you.", "success");
    }
  } catch (e) {
    console.error("Review submit error:", e);
  }
}

async function openHistoryDrawer() {
  sound.play('click');
  try {
    const res = await fetch(`/api/rides/history?user_id=${state.user.id}`);
    if (res.ok) {
      const history = await res.json();
      const listEl = document.getElementById('history-list-container');
      if (history.length === 0) {
        listEl.innerHTML = '<p class="empty-text">No trips completed yet.</p>';
      } else {
        listEl.innerHTML = '';
        history.forEach(r => {
          const item = document.createElement('div');
          item.className = 'history-item-card';
          item.innerHTML = `
            <div class="history-item-header">
              <span class="h-date">${new Date(r.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
              <span class="h-fare">₹${Math.round(r.fare_actual || r.fare_estimate).toLocaleString('en-IN')}</span>
            </div>
            <div class="h-route">
              <div>📍 ${r.pickup_name}</div>
              <div>🎯 ${r.drop_name}</div>
            </div>
            <div class="h-meta">
              <span>${r.distance_km} km</span> • <span>${r.vehicle_type.toUpperCase()}</span> • <span class="h-status">${r.status}</span>
            </div>
          `;
          listEl.appendChild(item);
        });
      }
      document.getElementById('history-drawer').classList.remove('hidden');
    }
  } catch (e) {
    console.error("History error:", e);
  }
}

// ==========================================================================
// 14. Toast Notification Utility
// ==========================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast-msg toast-${type}`;
  toast.innerHTML = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ==========================================================================
// 15. DOM Event Listeners & Startup
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Map & Keys
  mapMgr.init();

  // 2. Setup City Selector
  const citySelect = document.getElementById('city-select');
  citySelect.addEventListener('change', (e) => {
    sound.play('click');
    setCity(e.target.value);
  });
  setCity('bengaluru');

  // 3. Map Style / Terrain selector
  const mapStyleSelect = document.getElementById('map-style-select');
  mapStyleSelect.addEventListener('change', (e) => {
    sound.play('click');
    const style = e.target.value;
    mapMgr.setLeafletStyle(style);
    showToast(`🗺️ Map style set to ${mapStyleSelect.options[mapStyleSelect.selectedIndex].text}`, "info");
  });

  // 4. Mode Switcher Tabs
  document.getElementById('tab-rider').addEventListener('click', () => switchMode('rider'));
  document.getElementById('tab-driver').addEventListener('click', () => switchMode('driver'));
  document.getElementById('tab-radar').addEventListener('click', () => switchMode('radar'));

  function switchMode(mode) {
    sound.play('click');
    state.currentMode = mode;
    ['tab-rider', 'tab-driver', 'tab-radar'].forEach(t => document.getElementById(t).classList.remove('active'));
    document.getElementById(`tab-${mode}`).classList.add('active');

    ['rider-panel', 'driver-panel', 'radar-panel'].forEach(p => document.getElementById(p).classList.add('hidden'));
    document.getElementById(`${mode}-panel`).classList.remove('hidden');

    if (mode === 'driver') loadDriverMetrics();
    if (mode === 'radar') fetchNearbyDrivers();
  }

  // 5. Tier Card Selection
  document.querySelectorAll('.tier-card').forEach(card => {
    card.addEventListener('click', () => {
      sound.play('click');
      document.querySelectorAll('.tier-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      state.selectedTier = card.dataset.tier;
      updateRequestButtonLabel();
      mapMgr.updatePickupDropMarkers();
    });
  });

  // 6. Payment Mode Quick Pills
  document.getElementById('paymode-razorpay').addEventListener('click', () => {
    sound.play('click');
    state.paymentMode = "razorpay";
    document.getElementById('paymode-razorpay').classList.add('active');
    document.getElementById('paymode-cash').classList.remove('active');
    updateRequestButtonLabel();
  });
  document.getElementById('paymode-cash').addEventListener('click', () => {
    sound.play('click');
    state.paymentMode = "cash";
    document.getElementById('paymode-cash').classList.add('active');
    document.getElementById('paymode-razorpay').classList.remove('active');
    updateRequestButtonLabel();
  });

  // 7. Request Ride Button
  document.getElementById('btn-request-ride').addEventListener('click', handleRequestRide);

  // 8. Driver Cockpit Controls
  document.getElementById('btn-driver-accept').addEventListener('click', handleDriverAccept);
  document.getElementById('btn-driver-decline').addEventListener('click', () => {
    sound.play('click');
    document.getElementById('driver-incoming-card').classList.add('hidden');
    if (state.dispatchTimerInterval) clearInterval(state.dispatchTimerInterval);
  });
  document.getElementById('btn-driver-step-arrived').addEventListener('click', handleDriverArrivedAtPickup);
  document.getElementById('btn-verify-otp').addEventListener('click', handleVerifyDriverOtp);
  document.getElementById('btn-driver-step-start').addEventListener('click', handleVerifyDriverOtp);
  document.getElementById('btn-driver-step-complete').addEventListener('click', handleDriverCompleteTrip);

  // 9. Location Picking on Map
  document.getElementById('btn-pick-origin').addEventListener('click', () => {
    sound.play('click');
    state.pickMode = 'pickup';
    document.getElementById('btn-pick-origin').classList.add('active-pick');
    showToast("📍 Click anywhere on the map to choose Pickup", "info");
  });
  document.getElementById('btn-pick-dest').addEventListener('click', () => {
    sound.play('click');
    state.pickMode = 'drop';
    document.getElementById('btn-pick-dest').classList.add('active-pick');
    showToast("🎯 Click anywhere on the map to choose Destination", "info");
  });

  // 10. Live GPS Geolocation
  const locateUserGPS = () => {
    sound.play('click');
    if (navigator.geolocation) {
      showToast("🛰️ Detecting real GPS position...", "info");
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = parseFloat(pos.coords.latitude.toFixed(5));
          const lng = parseFloat(pos.coords.longitude.toFixed(5));
          state.pickup = {
            name: `My GPS Location [${lat}, ${lng}]`,
            lat: lat,
            lng: lng
          };
          const pickupInp = document.getElementById('pickup-input');
          pickupInp.value = state.pickup.name;
          const pClear = document.getElementById('btn-clear-pickup');
          if (pClear) pClear.classList.remove('hidden');
          mapMgr.updatePickupDropMarkers();
          if (mapMgr.leafletMap) mapMgr.leafletMap.flyTo([lat, lng], 15);
          if (mapMgr.googleMap) {
            mapMgr.googleMap.setCenter({ lat, lng });
            mapMgr.googleMap.setZoom(15);
          }
          fetchFareEstimate();
          fetchNearbyDrivers();
          showToast("🛰️ Resolving street address...", "info");

          reverseGeocodeLocation(lat, lng).then(geo => {
            if (geo && geo.name) {
              state.pickup.name = geo.name;
              pickupInp.value = geo.name;
              mapMgr.updatePickupDropMarkers();
              showToast(`✅ GPS locked: ${geo.name.split(',')[0]}`, "success");
            } else {
              showToast("✅ Real GPS position locked!", "success");
            }
          });
        },
        (err) => {
          showToast("GPS permission denied or unavailable. Using city center.", "alert");
        }
      );
    }
  };
  document.getElementById('btn-gps-current').addEventListener('click', locateUserGPS);
  document.getElementById('btn-gps-map').addEventListener('click', locateUserGPS);

  // 11. Recenter Buttons
  document.getElementById('btn-pan-india').addEventListener('click', () => mapMgr.viewWholeIndia());
  document.getElementById('btn-recenter-map').addEventListener('click', () => mapMgr.centerCity(state.currentCity));

  // 12. Modals Management
  // API Keys
  document.getElementById('btn-open-api-keys').addEventListener('click', () => {
    sound.play('click');
    updateConfigModalInputs();
    document.getElementById('api-keys-modal').classList.remove('hidden');
  });
  document.getElementById('btn-close-api-keys').addEventListener('click', () => {
    document.getElementById('api-keys-modal').classList.add('hidden');
  });
  document.getElementById('btn-cancel-api-keys').addEventListener('click', () => {
    document.getElementById('api-keys-modal').classList.add('hidden');
  });
  document.getElementById('btn-save-api-keys').addEventListener('click', handleSaveApiKeys);

  // Payments & Reviews
  document.getElementById('btn-open-payment').addEventListener('click', () => {
    sound.play('click');
    const fare = state.activeRide ? (state.activeRide.fare_actual || state.activeRide.fare_estimate || 580) : 580;
    document.getElementById('pay-modal-amount').innerText = `₹${Math.round(fare).toLocaleString('en-IN')}`;
    updatePayButtonText();
    document.getElementById('payment-modal').classList.remove('hidden');
  });
  document.getElementById('btn-close-payment').addEventListener('click', () => {
    document.getElementById('payment-modal').classList.add('hidden');
  });
  document.getElementById('btn-confirm-payment').addEventListener('click', handleConfirmPayment);

  // Tip Selection Chips
  document.querySelectorAll('.tip-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      sound.play('click');
      document.querySelectorAll('.tip-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      updatePayButtonText();
    });
  });

  // Payment Method Options in Modal
  document.querySelectorAll('.payment-method-selector .method-option').forEach(opt => {
    opt.addEventListener('click', () => {
      sound.play('click');
      document.querySelectorAll('.payment-method-selector .method-option').forEach(o => {
        o.classList.remove('active');
        o.querySelector('.check-mark').innerText = '';
      });
      opt.classList.add('active');
      opt.querySelector('.check-mark').innerText = '✓';
      updatePayButtonText();
    });
  });

  // Initialize Razorpay Sandbox Checkout Listeners
  initRazorpaySandboxListeners();

  // Receipts
  document.getElementById('btn-open-receipt').addEventListener('click', openReceiptModal);
  document.getElementById('btn-close-receipt').addEventListener('click', () => {
    document.getElementById('receipt-modal').classList.add('hidden');
  });
  document.getElementById('btn-print-receipt').addEventListener('click', () => {
    window.print();
  });

  // History Drawer
  document.getElementById('btn-open-history').addEventListener('click', openHistoryDrawer);
  document.getElementById('btn-close-history').addEventListener('click', () => {
    document.getElementById('history-drawer').classList.add('hidden');
  });

  // Review & Rating
  document.getElementById('btn-close-review').addEventListener('click', () => {
    document.getElementById('review-modal').classList.add('hidden');
  });
  document.getElementById('btn-submit-review').addEventListener('click', handleSubmitReview);
  document.querySelectorAll('#star-rating-row .star').forEach(star => {
    star.addEventListener('click', () => {
      sound.play('click');
      const val = parseInt(star.dataset.star);
      document.querySelectorAll('#star-rating-row .star').forEach(s => {
        if (parseInt(s.dataset.star) <= val) s.classList.add('selected');
        else s.classList.remove('selected');
      });
    });
  });
  document.querySelectorAll('.review-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      sound.play('click');
      tag.classList.toggle('active');
    });
  });

  // Driver Chat & Call Simulation
  document.getElementById('btn-call-driver').addEventListener('click', () => {
    sound.play('accept');
    showToast("📞 Calling Driver Partner (+91 98450 11007)... [Simulated audio relay active]", "success");
  });
  document.getElementById('btn-msg-driver').addEventListener('click', () => {
    sound.play('click');
    document.getElementById('chat-modal').classList.remove('hidden');
  });
  document.getElementById('btn-close-chat').addEventListener('click', () => {
    document.getElementById('chat-modal').classList.add('hidden');
  });
  document.querySelectorAll('.chat-quick-replies .quick-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      sound.play('click');
      sendChatMessage(chip.dataset.text);
    });
  });
  document.getElementById('btn-send-chat').addEventListener('click', () => {
    const inp = document.getElementById('chat-text-input');
    if (inp.value.trim()) {
      sendChatMessage(inp.value.trim());
      inp.value = '';
    }
  });

  function sendChatMessage(text) {
    sound.play('click');
    const container = document.getElementById('chat-messages-container');
    const msg = document.createElement('div');
    msg.className = 'chat-msg rider-msg';
    msg.innerHTML = `<span class="msg-sender">You</span><span class="msg-bubble">${text}</span>`;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;

    // Simulate driver reply
    setTimeout(() => {
      sound.play('accept');
      const reply = document.createElement('div');
      reply.className = 'chat-msg driver-msg';
      reply.innerHTML = `<span class="msg-sender">Driver</span><span class="msg-bubble">Understood! I will be there in a moment.</span>`;
      container.appendChild(reply);
      container.scrollTop = container.scrollHeight;
    }, 1200);
  }

  // ==========================================================================
  // 14. Full Authentication System & Indian Face Avatar Manager
  // ==========================================================================
  const CURATED_INDIAN_AVATARS = [
    { name: "Priya Sharma", role: "rider", url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80" },
    { name: "Capt. Vikram Rathore", role: "pilot", url: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80" },
    { name: "Rajesh Kumar", role: "driver", url: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80" },
    { name: "Capt. Priya Sen", role: "driver", url: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&auto=format&fit=crop&q=80" },
    { name: "Manjunath Gowda", role: "driver", url: "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80" },
    { name: "Sunil Gowda", role: "driver", url: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80" },
    { name: "Ananya Roy", role: "rider", url: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80" },
    { name: "Deepak Rao", role: "driver", url: "https://images.unsplash.com/photo-1528892952291-009c663ce843?w=200&auto=format&fit=crop&q=80" }
  ];

  let selectedRegisterAvatar = CURATED_INDIAN_AVATARS[0].url;

  function updateUserNavUI() {
    const u = state.user;
    if (!u) return;

    const navImg = document.getElementById('nav-user-img');
    const navFallback = document.getElementById('nav-user-avatar');
    const navName = document.getElementById('nav-user-name');
    const navRole = document.getElementById('nav-user-role');

    if (u.profile_pic) {
      if (navImg) {
        navImg.src = u.profile_pic;
        navImg.classList.remove('hidden');
      }
      if (navFallback) navFallback.classList.add('hidden');
    } else {
      if (navImg) navImg.classList.add('hidden');
      if (navFallback) {
        navFallback.classList.remove('hidden');
        navFallback.innerText = u.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      }
    }

    if (navName) navName.innerText = u.name;
    if (navRole) navRole.innerText = u.role === 'driver' ? 'Driver Partner (Pilot)' : 'Passenger (India)';

    // Dropdown details
    const dropImg = document.getElementById('dropdown-user-img');
    const dropName = document.getElementById('dropdown-user-name');
    const dropEmail = document.getElementById('dropdown-user-email');
    const dropRole = document.getElementById('dropdown-user-role');
    const dropRating = document.getElementById('dropdown-user-rating');

    if (dropImg && u.profile_pic) dropImg.src = u.profile_pic;
    if (dropName) dropName.innerText = u.name;
    if (dropEmail) dropEmail.innerText = u.email || `${u.name.toLowerCase().replace(' ', '.')}@aerocabs.in`;
    if (dropRole) dropRole.innerText = u.role ? u.role.toUpperCase() : 'RIDER';
    if (dropRating) dropRating.innerText = `★ ${u.rating_avg || 4.95} Rating`;

    // Highlight active chip
    document.querySelectorAll('.persona-chip-btn').forEach(btn => {
      const btnId = parseInt(btn.dataset.userid);
      btn.classList.toggle('active', btnId === u.id);
    });
  }

  function initAuthSystem() {
    // 1. Initial UI update
    updateUserNavUI();

    // 2. Persona Pill toggle dropdown
    const pill = document.getElementById('current-user-pill');
    const dropdown = document.getElementById('user-profile-dropdown');
    if (pill && dropdown) {
      pill.addEventListener('click', (e) => {
        e.stopPropagation();
        sound.play('click');
        dropdown.classList.toggle('hidden');
      });
      document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && !pill.contains(e.target)) {
          dropdown.classList.add('hidden');
        }
      });
    }

    // 3. Quick Persona Switchers
    document.querySelectorAll('.persona-chip-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        sound.play('click');
        const userId = parseInt(btn.dataset.userid);
        await switchPersona(userId);
        if (dropdown) dropdown.classList.add('hidden');
      });
    });

    // 4. Dropdown action buttons
    const btnDropSignIn = document.getElementById('btn-dropdown-signin');
    const btnDropReg = document.getElementById('btn-dropdown-register');
    const btnDropLogout = document.getElementById('btn-dropdown-logout');
    const authModal = document.getElementById('auth-modal');

    if (btnDropSignIn && authModal) {
      btnDropSignIn.addEventListener('click', (e) => {
        e.stopPropagation();
        sound.play('click');
        dropdown.classList.add('hidden');
        openAuthModal('login');
      });
    }
    if (btnDropReg && authModal) {
      btnDropReg.addEventListener('click', (e) => {
        e.stopPropagation();
        sound.play('click');
        dropdown.classList.add('hidden');
        openAuthModal('register');
      });
    }
    if (btnDropLogout) {
      btnDropLogout.addEventListener('click', (e) => {
        e.stopPropagation();
        sound.play('click');
        dropdown.classList.add('hidden');
        localStorage.removeItem('flying_cabs_user');
        localStorage.removeItem('flying_cabs_token');
        showToast("Signed out. Please sign in to book rides.", "info");
        openAuthModal('login');
      });
    }

    // 5. Auth Modal tabs and inputs
    const btnCloseAuth = document.getElementById('btn-close-auth');
    if (btnCloseAuth && authModal) {
      btnCloseAuth.addEventListener('click', () => authModal.classList.add('hidden'));
    }

    const tabLogin = document.getElementById('tab-auth-login');
    const tabRegister = document.getElementById('tab-auth-register');
    const formLogin = document.getElementById('form-auth-login');
    const formRegister = document.getElementById('form-auth-register');

    if (tabLogin && tabRegister) {
      tabLogin.addEventListener('click', () => {
        sound.play('click');
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        formLogin.classList.remove('hidden');
        formRegister.classList.add('hidden');
      });
      tabRegister.addEventListener('click', () => {
        sound.play('click');
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        formRegister.classList.remove('hidden');
        formLogin.classList.add('hidden');
      });
    }

    // Role radio buttons in registration
    const radioRider = document.querySelector('input[name="reg_role"][value="rider"]');
    const radioDriver = document.querySelector('input[name="reg_role"][value="driver"]');
    const driverFields = document.getElementById('driver-signup-section');
    const labelRider = document.getElementById('label-role-rider');
    const labelDriver = document.getElementById('label-role-driver');

    if (radioRider && radioDriver) {
      radioRider.addEventListener('change', () => {
        labelRider.classList.add('active');
        labelDriver.classList.remove('active');
        if (driverFields) driverFields.classList.add('hidden');
      });
      radioDriver.addEventListener('change', () => {
        labelDriver.classList.add('active');
        labelRider.classList.remove('active');
        if (driverFields) driverFields.classList.remove('hidden');
      });
    }

    // Populate Curated Indian Face Avatars
    renderAvatarPickerGrid();

    // Demo quick login buttons on login tab
    document.querySelectorAll('.demo-chip-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        sound.play('click');
        const role = btn.dataset.demo;
        if (role === 'rider') {
          document.getElementById('login-ident').value = 'aarav.sharma@aerocabs.in';
        } else if (role === 'pilot') {
          document.getElementById('login-ident').value = 'vikram.rathore@aerocabs.in';
        } else if (role === 'driver') {
          document.getElementById('login-ident').value = 'rajesh.kumar@aerocabs.in';
        }
        document.getElementById('login-pass').value = 'demo123';
      });
    });

    // Form submit: Login
    if (formLogin) {
      formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        sound.play('click');
        const ident = document.getElementById('login-ident').value.trim();
        const pass = document.getElementById('login-pass').value;

        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_or_phone: ident, password: pass })
          });
          const data = await res.json();
          if (res.ok) {
            state.user = data.user;
            localStorage.setItem('flying_cabs_user', JSON.stringify(data.user));
            localStorage.setItem('flying_cabs_token', data.token);
            updateUserNavUI();
            authModal.classList.add('hidden');
            showToast(`✅ ${data.message}`, "success");
            if (data.user.role === 'driver') {
              switchMode('driver');
            } else {
              switchMode('rider');
            }
          } else {
            showToast(`Login failed: ${data.detail || "Please check credentials"}`, "alert");
          }
        } catch (err) {
          console.error(err);
          showToast("Network connection error.", "alert");
        }
      });
    }

    // Form submit: Register
    if (formRegister) {
      formRegister.addEventListener('submit', async (e) => {
        e.preventDefault();
        sound.play('click');
        const name = document.getElementById('reg-name').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const phone = document.getElementById('reg-phone').value.trim();
        const password = document.getElementById('reg-pass').value;
        const role = document.querySelector('input[name="reg_role"]:checked').value;
        const customUrl = document.getElementById('reg-custom-avatar').value.trim();
        const profilePic = customUrl || selectedRegisterAvatar;

        const payload = {
          name,
          email,
          phone,
          password,
          role,
          profile_pic: profilePic
        };

        if (role === 'driver') {
          payload.vehicle_type = document.getElementById('reg-vehicle-type').value;
          payload.vehicle_info = document.getElementById('reg-car-model').value.trim() || 'Tata Tigor EV Prime';
          payload.license_plate = document.getElementById('reg-license-plate').value.trim() || 'KA-05-EV-4242';
        }

        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (res.ok) {
            state.user = data.user;
            localStorage.setItem('flying_cabs_user', JSON.stringify(data.user));
            localStorage.setItem('flying_cabs_token', data.token);
            updateUserNavUI();
            authModal.classList.add('hidden');
            showToast(`🎉 ${data.message}`, "success");
            if (data.user.role === 'driver') {
              switchMode('driver');
            } else {
              switchMode('rider');
            }
          } else {
            showToast(`Registration failed: ${data.detail || "Error creating account"}`, "alert");
          }
        } catch (err) {
          console.error(err);
          showToast("Registration network error.", "alert");
        }
      });
    }
  }

  function renderAvatarPickerGrid() {
    const grid = document.getElementById('avatar-picker-grid');
    if (!grid) return;
    grid.innerHTML = '';

    CURATED_INDIAN_AVATARS.forEach((av, idx) => {
      const item = document.createElement('div');
      item.className = `avatar-pick-item ${idx === 0 ? 'active' : ''}`;
      item.innerHTML = `
        <img src="${av.url}" alt="${av.name}" class="avatar-pick-img">
        <span class="avatar-pick-name">${av.name.split(' ')[0]}</span>
      `;
      item.addEventListener('click', () => {
        sound.play('click');
        document.querySelectorAll('.avatar-pick-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        selectedRegisterAvatar = av.url;
      });
      grid.appendChild(item);
    });
  }

  function openAuthModal(tab = 'login') {
    const authModal = document.getElementById('auth-modal');
    if (!authModal) return;
    authModal.classList.remove('hidden');

    const tabLogin = document.getElementById('tab-auth-login');
    const tabRegister = document.getElementById('tab-auth-register');
    const formLogin = document.getElementById('form-auth-login');
    const formRegister = document.getElementById('form-auth-register');

    if (tab === 'login') {
      tabLogin.classList.add('active');
      tabRegister.classList.remove('active');
      formLogin.classList.remove('hidden');
      formRegister.classList.add('hidden');
    } else {
      tabRegister.classList.add('active');
      tabLogin.classList.remove('active');
      formRegister.classList.remove('hidden');
      formLogin.classList.add('hidden');
    }
  }

  async function switchPersona(userId) {
    try {
      const res = await fetch(`/api/auth/quick-switch/${userId}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        state.user = data.user;
        localStorage.setItem('flying_cabs_user', JSON.stringify(data.user));
        localStorage.setItem('flying_cabs_token', data.token);
        updateUserNavUI();
        showToast(`⚡ ${data.message}`, "success");

        if (data.user.role === 'driver') {
          switchMode('driver');
        } else {
          switchMode('rider');
        }
      }
    } catch (e) {
      console.error("Switch error:", e);
    }
  }

  // ==========================================================================
  // 15. Pan-India Location Autocomplete Engine (Index + Live Nominatim)
  // ==========================================================================
  // ==========================================================================
  // 15. Pan-India Location Autocomplete Engine (API + Index + Fallback)
  // ==========================================================================
  function initPanIndiaAutocomplete() {
    const pickupInp = document.getElementById('pickup-input');
    const pickupDrop = document.getElementById('pickup-autocomplete');
    const pickupClear = document.getElementById('btn-clear-pickup');
    const pickupSpinner = document.getElementById('pickup-spinner');

    const dropInp = document.getElementById('drop-input');
    const dropDrop = document.getElementById('drop-autocomplete');
    const dropClear = document.getElementById('btn-clear-drop');
    const dropSpinner = document.getElementById('drop-spinner');

    const swapBtn = document.getElementById('btn-swap-locations');

    // 1. Setup Autocomplete for Pickup (Source)
    setupLocationAutocomplete({
      type: 'pickup',
      inputEl: pickupInp,
      dropdownEl: pickupDrop,
      clearBtn: pickupClear,
      spinnerEl: pickupSpinner,
      onSelect: (loc) => {
        state.pickup = { name: loc.name, lat: loc.lat, lng: loc.lng };
        pickupInp.value = loc.name;
        if (pickupClear) pickupClear.classList.remove('hidden');
        mapMgr.updatePickupDropMarkers();
        if (mapMgr.leafletMap) mapMgr.leafletMap.flyTo([loc.lat, loc.lng], 14);
        if (mapMgr.googleMap) {
          mapMgr.googleMap.panTo({ lat: loc.lat, lng: loc.lng });
          mapMgr.googleMap.setZoom(14);
        }
        fetchFareEstimate();
        fetchNearbyDrivers();
        const prefix = loc.category === 'pincode' ? '📮 PIN Code Pickup' : '📍 Pickup';
        showToast(`${prefix} set to ${loc.name.split(',')[0]}`, "info");
      }
    });

    // 2. Setup Autocomplete for Destination (Drop)
    setupLocationAutocomplete({
      type: 'drop',
      inputEl: dropInp,
      dropdownEl: dropDrop,
      clearBtn: dropClear,
      spinnerEl: dropSpinner,
      onSelect: (loc) => {
        state.drop = { name: loc.name, lat: loc.lat, lng: loc.lng };
        dropInp.value = loc.name;
        if (dropClear) dropClear.classList.remove('hidden');
        mapMgr.updatePickupDropMarkers();
        if (mapMgr.leafletMap) mapMgr.leafletMap.flyTo([loc.lat, loc.lng], 14);
        if (mapMgr.googleMap) {
          mapMgr.googleMap.panTo({ lat: loc.lat, lng: loc.lng });
          mapMgr.googleMap.setZoom(14);
        }
        fetchFareEstimate();
        fetchNearbyDrivers();
        const prefix = loc.category === 'pincode' ? '🎯 Destination PIN' : '🎯 Destination';
        showToast(`${prefix} set to ${loc.name.split(',')[0]}`, "info");
      }
    });

    // 3. Swap Source & Destination Button
    if (swapBtn) {
      swapBtn.addEventListener('click', () => {
        sound.play('click');
        if (!state.pickup || !state.drop) return;

        // Animate button
        swapBtn.style.transform = 'scale(0.9) rotate(180deg)';
        setTimeout(() => { swapBtn.style.transform = ''; }, 300);

        // Swap state
        const temp = { ...state.pickup };
        state.pickup = { ...state.drop };
        state.drop = temp;

        // Update inputs
        pickupInp.value = state.pickup.name;
        dropInp.value = state.drop.name;
        if (pickupClear) pickupClear.classList.remove('hidden');
        if (dropClear) dropClear.classList.remove('hidden');

        // Update map & fares
        mapMgr.updatePickupDropMarkers();
        fetchFareEstimate();
        showToast("⇅ Source & Destination swapped!", "info");
      });
    }

    // 4. Interactive Quick Postal PIN Code Chips
    const pinChips = document.querySelectorAll('#pincode-quick-chips .pin-chip');
    pinChips.forEach(chip => {
      chip.addEventListener('click', async () => {
        sound.play('click');
        const pin = chip.dataset.pin;
        if (!pin) return;

        // Choose target: drop if drop input is active or pickup is already filled
        const isDropTarget = (document.activeElement === dropInp) || (pickupInp && pickupInp.value && (!dropInp || !dropInp.value));
        const targetType = isDropTarget ? 'drop' : 'pickup';
        const targetInput = isDropTarget ? dropInp : pickupInp;
        const targetClear = isDropTarget ? dropClear : pickupClear;

        try {
          const res = await fetch(`/api/locations/pincode/${pin}`);
          if (res.ok) {
            const loc = await res.json();
            if (targetType === 'pickup') {
              state.pickup = { name: loc.name, lat: loc.lat, lng: loc.lng };
              pickupInp.value = loc.name;
              if (pickupClear) pickupClear.classList.remove('hidden');
            } else {
              state.drop = { name: loc.name, lat: loc.lat, lng: loc.lng };
              dropInp.value = loc.name;
              if (dropClear) dropClear.classList.remove('hidden');
            }
            mapMgr.updatePickupDropMarkers();
            if (mapMgr.leafletMap) mapMgr.leafletMap.flyTo([loc.lat, loc.lng], 14);
            fetchFareEstimate();
            fetchNearbyDrivers();
            showToast(`📮 PIN Code [${pin}] applied to ${targetType.toUpperCase()}: ${loc.name.split(',')[0]}`, "info");
          }
        } catch (err) {
          console.error("PIN chip lookup failed:", err);
        }
      });
    });

    // Initialize clear button states based on initial values
    if (pickupInp && pickupClear && pickupInp.value) pickupClear.classList.remove('hidden');
    if (dropInp && dropClear && dropInp.value) dropClear.classList.remove('hidden');
  }

  function setupLocationAutocomplete({ type, inputEl, dropdownEl, clearBtn, spinnerEl, onSelect }) {
    if (!inputEl || !dropdownEl) return;
    let debounceTimer = null;
    let activeIndex = -1;
    let currentItems = [];

    const showSpinner = () => { if (spinnerEl) spinnerEl.classList.remove('hidden'); };
    const hideSpinner = () => { if (spinnerEl) spinnerEl.classList.add('hidden'); };

    async function searchLocations(query) {
      const q = query.trim();
      if (!q) return [];
      showSpinner();
      try {
        const cityParam = state.currentCity ? `&city=${encodeURIComponent(state.currentCity)}` : '';
        const res = await fetch(`/api/locations/search?q=${encodeURIComponent(q)}${cityParam}`);
        hideSpinner();
        if (res.ok) {
          const items = await res.json();
          if (items && items.length > 0) return items;
        }
      } catch (err) {
        hideSpinner();
      }

      // Fallback: search local curated index
      const qLow = q.toLowerCase();
      return INDIAN_LOCATIONS_INDEX.filter(item =>
        item.name.toLowerCase().includes(qLow) || (item.sub && item.sub.toLowerCase().includes(qLow))
      ).slice(0, 6);
    }

    async function showPopularHotspots() {
      try {
        const cityParam = state.currentCity ? `?city=${encodeURIComponent(state.currentCity)}` : '';
        const res = await fetch(`/api/locations/hotspots${cityParam}`);
        if (res.ok) {
          const hotspots = await res.json();
          if (hotspots && hotspots.length > 0) {
            currentItems = hotspots;
            activeIndex = -1;
            renderAutocompleteList(dropdownEl, hotspots, inputEl, onSelect, activeIndex, "POPULAR IN " + (state.currentCity || "CITY").toUpperCase());
            return;
          }
        }
      } catch (e) {}

      const fallback = INDIAN_LOCATIONS_INDEX.slice(0, 5);
      currentItems = fallback;
      activeIndex = -1;
      renderAutocompleteList(dropdownEl, fallback, inputEl, onSelect, activeIndex, "POPULAR LOCATIONS");
    }

    // Input Event
    inputEl.addEventListener('input', () => {
      const q = inputEl.value.trim();
      if (clearBtn) {
        if (q.length > 0) clearBtn.classList.remove('hidden');
        else clearBtn.classList.add('hidden');
      }

      clearTimeout(debounceTimer);
      if (q.length < 2) {
        if (q.length === 0) {
          showPopularHotspots();
        } else {
          dropdownEl.classList.add('hidden');
        }
        return;
      }

      const isPinInput = /^\d{3,6}$/.test(q);
      const delay = isPinInput ? 80 : 160;
      debounceTimer = setTimeout(async () => {
        const items = await searchLocations(q);
        currentItems = items;
        activeIndex = -1;
        const header = (/^\d{6}$/.test(q) || (items && items.length > 0 && items[0].category === 'pincode')) ? "📮 POSTAL PIN CODE RESULTS" : null;
        renderAutocompleteList(dropdownEl, items, inputEl, onSelect, activeIndex, header, q);
      }, delay);
    });

    // Focus Event
    inputEl.addEventListener('focus', () => {
      const q = inputEl.value.trim();
      if (q.length >= 2) {
        searchLocations(q).then(items => {
          currentItems = items;
          activeIndex = -1;
          const header = (/^\d{6}$/.test(q) || (items && items.length > 0 && items[0].category === 'pincode')) ? "📮 POSTAL PIN CODE RESULTS" : null;
          renderAutocompleteList(dropdownEl, items, inputEl, onSelect, activeIndex, header, q);
        });
      } else {
        showPopularHotspots();
      }
    });

    // Clear Button
    if (clearBtn) {
      clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        inputEl.value = '';
        clearBtn.classList.add('hidden');
        inputEl.focus();
        showPopularHotspots();
      });
    }

    // Keyboard Navigation
    inputEl.addEventListener('keydown', async (e) => {
      if (dropdownEl.classList.contains('hidden') && e.key !== 'Enter') return;

      const rows = dropdownEl.querySelectorAll('.autocomplete-item');

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (rows.length === 0) return;
        activeIndex = (activeIndex + 1) % rows.length;
        updateActiveItemHighlight(rows, activeIndex);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (rows.length === 0) return;
        activeIndex = (activeIndex - 1 + rows.length) % rows.length;
        updateActiveItemHighlight(rows, activeIndex);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < currentItems.length) {
          sound.play('click');
          onSelect(currentItems[activeIndex]);
          dropdownEl.classList.add('hidden');
        } else if (currentItems.length > 0) {
          sound.play('click');
          onSelect(currentItems[0]);
          dropdownEl.classList.add('hidden');
        } else {
          const q = inputEl.value.trim();
          if (q.length >= 2) {
            showSpinner();
            // Direct fast PIN code lookup if 6 digits
            if (/^[1-9][0-9]{5}$/.test(q)) {
              try {
                const pRes = await fetch(`/api/locations/pincode/${q}`);
                if (pRes.ok) {
                  const pItem = await pRes.json();
                  hideSpinner();
                  sound.play('click');
                  onSelect(pItem);
                  dropdownEl.classList.add('hidden');
                  return;
                }
              } catch (e) {}
            }
            const items = await searchLocations(q);
            hideSpinner();
            if (items && items.length > 0) {
              sound.play('click');
              onSelect(items[0]);
              dropdownEl.classList.add('hidden');
            } else {
              showToast("Location not found. Try 6-digit PIN, landmark or city.", "alert");
            }
          }
        }
      } else if (e.key === 'Escape') {
        dropdownEl.classList.add('hidden');
      }
    });

    // Blur / Change
    inputEl.addEventListener('change', async () => {
      const q = inputEl.value.trim();
      if (!q) return;
      const currentLoc = (type === 'pickup') ? state.pickup : state.drop;
      if (!currentLoc || currentLoc.name !== q) {
        if (/^[1-9][0-9]{5}$/.test(q)) {
          try {
            const pRes = await fetch(`/api/locations/pincode/${q}`);
            if (pRes.ok) {
              const pItem = await pRes.json();
              onSelect(pItem);
              return;
            }
          } catch (e) {}
        }
        const items = await searchLocations(q);
        if (items && items.length > 0) {
          onSelect(items[0]);
        }
      }
    });

    // Click Outside
    document.addEventListener('click', (e) => {
      if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target) && (!clearBtn || !clearBtn.contains(e.target))) {
        dropdownEl.classList.add('hidden');
      }
    });
  }

  function updateActiveItemHighlight(rows, activeIdx) {
    rows.forEach((r, idx) => {
      if (idx === activeIdx) {
        r.classList.add('active-item');
        r.scrollIntoView({ block: 'nearest' });
      } else {
        r.classList.remove('active-item');
      }
    });
  }

  function renderAutocompleteList(dropdownEl, items, inputEl, onSelect, activeIndex = -1, headerText = null, queryText = "") {
    dropdownEl.innerHTML = '';
    if (!items || items.length === 0) {
      const emptyRow = document.createElement('div');
      emptyRow.className = 'autocomplete-empty-row';
      emptyRow.style.padding = '12px 14px';
      emptyRow.style.fontSize = '0.8rem';
      emptyRow.style.color = 'var(--text-dim)';
      emptyRow.innerText = 'No matches found in India. Try 6-digit PIN code, landmark, or city name.';
      dropdownEl.appendChild(emptyRow);
      dropdownEl.classList.remove('hidden');
      return;
    }

    if (headerText) {
      const hdr = document.createElement('div');
      hdr.className = 'autocomplete-header-label';
      hdr.style.padding = '6px 12px';
      hdr.style.fontSize = '0.68rem';
      hdr.style.fontWeight = '700';
      hdr.style.letterSpacing = '0.5px';
      hdr.style.color = 'var(--cyan-primary)';
      hdr.style.background = 'rgba(0, 240, 255, 0.08)';
      hdr.innerText = headerText;
      dropdownEl.appendChild(hdr);
    }

    items.forEach((item, idx) => {
      const row = document.createElement('div');
      row.className = `autocomplete-item ${idx === activeIndex ? 'active-item' : ''}`;

      let catBadge = '';
      if (item.category === 'pincode') catBadge = '<span class="auto-badge" style="color: #00f0ff; background: rgba(0, 240, 255, 0.18); border: 1px solid rgba(0, 240, 255, 0.35); font-weight: 700;">📮 PIN CODE</span>';
      else if (item.category === 'airport') catBadge = '<span class="auto-badge">AIRPORT</span>';
      else if (item.category === 'railway') catBadge = '<span class="auto-badge" style="color: #ffb703; background: rgba(255,183,3,0.15)">RAILWAY</span>';
      else if (item.category === 'tech') catBadge = '<span class="auto-badge" style="color: #00f59b; background: rgba(0,245,155,0.15)">TECH PARK</span>';
      else if (item.category === 'metro') catBadge = '<span class="auto-badge" style="color: #9d4edd; background: rgba(157,78,221,0.15)">METRO</span>';

      let displayName = item.name;
      if (queryText && queryText.length >= 2) {
        const regex = new RegExp(`(${queryText.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
        displayName = item.name.replace(regex, '<mark style="background: rgba(0,240,255,0.3); color: #fff; padding: 0 2px; border-radius: 2px;">$1</mark>');
      }

      row.innerHTML = `
        <span class="auto-icon">${item.icon || '📍'}</span>
        <div class="auto-details">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <span class="auto-name">${displayName}</span>
            ${catBadge}
          </div>
          <span class="auto-sub">${item.sub || 'India'}</span>
        </div>
      `;

      row.addEventListener('click', () => {
        sound.play('click');
        onSelect(item);
        dropdownEl.classList.add('hidden');
      });

      dropdownEl.appendChild(row);
    });

    const footer = document.createElement('div');
    footer.className = 'autocomplete-dropdown-footer';
    footer.innerHTML = `
      <span>⚡ Pan-India Geo Search</span>
      <span>Use ↑↓ to navigate • Enter to select</span>
    `;
    dropdownEl.appendChild(footer);

    dropdownEl.classList.remove('hidden');
  }

  // ==========================================================================
  // 16. Choice of Cars Showcase Modal Initializer
  // ==========================================================================
  function initFleetShowcaseModal() {
    const btnOpen = document.getElementById('btn-open-fleet-showcase');
    const modal = document.getElementById('fleet-showcase-modal');
    const btnClose = document.getElementById('btn-close-fleet-showcase');

    if (btnOpen && modal) {
      btnOpen.addEventListener('click', () => {
        sound.play('click');
        if (state.estimates) {
          renderFleetShowcase(state.estimates);
        }
        modal.classList.remove('hidden');
      });
    }
    if (btnClose && modal) {
      btnClose.addEventListener('click', () => modal.classList.add('hidden'));
    }
  }

  // Cancel Ride
  document.getElementById('btn-cancel-ride').addEventListener('click', async () => {
    sound.play('click');
    if (!state.activeRide) return;
    try {
      await fetch(`/api/rides/${state.activeRide.id}/cancel`, { method: 'POST' });
      document.getElementById('active-ride-card').classList.add('hidden');
      state.activeRide = null;
      showToast("Ride cancelled.", "alert");
    } catch (e) {
      console.error(e);
    }
  });

  // Auto-Pilot switch
  const simToggle = document.getElementById('sim-toggle');
  if (simToggle) {
    simToggle.addEventListener('change', (e) => {
      state.autoSimulate = e.target.checked;
      showToast(`Auto-Pilot simulation ${state.autoSimulate ? 'enabled' : 'disabled'}`, "info");
    });
  }

  // Initialize new systems
  initAuthSystem();
  initPanIndiaAutocomplete();
  initFleetShowcaseModal();

  // 17. Initialize WebSockets
  initWebSocket();
});
