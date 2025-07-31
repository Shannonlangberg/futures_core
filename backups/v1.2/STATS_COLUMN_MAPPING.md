# Futures Core - Stats Column Mapping

## 📊 Complete Field Alignment with Google Sheets

### **Google Sheets Column Structure:**

| Column | Field Name | Dashboard Display | Landing Page | Voice Recognition |
|--------|------------|------------------|--------------|------------------|
| **A** | Timestamp | _(system)_ | _(system)_ | _(automatic)_ |
| **B** | Date | _(system)_ | _(system)_ | _(automatic)_ |
| **C** | Campus | _(system)_ | _(dropdown)_ | _(detected/selected)_ |
| **D** | **Total Attendance** | Main stat card | 📍 Total Attendance | "total attendance was 150" |
| **E** | **First Time Visitors** | New People breakdown | 🆕 First Time | "first time visitors were 25" |
| **F** | **Visitors** | New People breakdown | 👥 Visitors | "visitors were 10" |
| **G** | **Information Gathered** | _(detailed view)_ | 📋 Info Gathered | "info gathered from 20" |
| **H** | **First Time Christians** | New Christians breakdown | ✨ First Time | "first time christians were 5" |
| **I** | **Rededications** | New Christians breakdown | 🔄 Rededications | "rededications were 3" |
| **J** | **Youth Attendance** | Youth breakdown | 🎯 Attendance | "youth attendance was 45" |
| **K** | **Youth Salvations** | Youth breakdown | ✨ Salvations | "youth salvations were 2" |
| **L** | **Youth New People** | Youth breakdown | 🆕 New People | "youth new people were 8" |
| **M** | **Kids Attendance** | Kids breakdown | 🧒 Attendance | "kids attendance was 35" |
| **N** | **Kids Leaders** | Kids breakdown | 👨‍🏫 Leaders | "kids leaders were 5" |
| **O** | **New Kids** | Kids breakdown | 🆕 New Kids | "new kids were 6" |
| **P** | **New Kids Salvations** | Kids breakdown | ✨ Salvations | "kids salvations were 1" |
| **Q** | **Connect Groups** | Individual stat card | 🤝 Connect Groups | "connect groups were 12" |
| **R** | **Dream Team** | Individual stat card | 🌟 Dream Team | "dream team members were 25" |
| **S** | **Tithe** | Financial data | _(Finance interface)_ | _(Finance team only)_ |
| **T** | **Baptisms** | Special events | 💧 Baptisms | "baptisms were 3" |
| **U** | **Child Dedications** | Special events | 👶 Child Dedications | "child dedications were 2" |

---

## 🔧 **System Features:**

### **✅ Dashboard Clickable Breakdowns:**
- **New People** → Shows First Time Visitors + Visitors + averages + insights
- **New Christians** → Shows First Time Christians + Rededications + averages + gospel impact
- **Youth** → Shows Attendance + Salvations + New People + averages + salvation rate
- **Kids** → Shows Attendance + Leaders + New Kids + Salvations + averages + ministry ratio

### **✅ Landing Page Stats Logging:**
- **All 20 stat fields** are clickable for direct logging
- **Campus validation** required before any logging
- **Voice recognition** supports all field patterns
- **Text input** supports all field patterns
- **Recent data display** shows current week's stats

### **✅ Finance Team Interface:**
- **Specialized tithe logging** for finance role only
- **Date selector** to choose service date
- **Multi-campus entry** on single interface
- **Updates existing rows** instead of creating duplicates
- **Shows current values** for selected date

### **✅ Voice Recognition Patterns:**
```
Total Attendance: "total attendance was 150", "150 people", "had 150"
First Time Visitors: "first time visitors were 25", "25 first timers", "25 newcomers"  
Visitors: "visitors were 10", "10 guests", "10 passing through"
Information Gathered: "info gathered from 20", "information gathered 20", "20 contact info"
First Time Christians: "first time christians were 5", "5 got saved", "5 new conversions"
Rededications: "rededications were 3", "3 came back", "3 recommitments"
Youth Attendance: "youth attendance was 45", "45 youth", "45 teens"
Youth Salvations: "youth salvations were 2", "2 youth saved", "2 teen decisions"
Youth New People: "youth new people were 8", "8 youth visitors", "8 new youth"
Kids Attendance: "kids attendance was 35", "35 kids", "35 children"
Kids Leaders: "kids leaders were 5", "5 kids helpers", "5 children leaders"
New Kids: "new kids were 6", "6 new children", "6 kids visitors"
Kids Salvations: "kids salvations were 1", "1 child saved", "1 kids decision"
Connect Groups: "connect groups were 12", "12 small groups", "12 life groups"
Dream Team: "dream team members were 25", "25 volunteers", "25 serving team"
Baptisms: "baptisms were 3", "3 baptized", "3 water baptism"
Child Dedications: "child dedications were 2", "2 baby dedications", "2 dedicated"
```

### **✅ Data Integrity:**
- **Backward compatibility** with legacy "New People", "New Christians", "Kids Total", "Volunteers" fields
- **Campus validation** prevents orphaned data
- **Role-based access** ensures proper permissions
- **Automatic calculations** for totals and averages

---

## 🎯 **Ready for Real Data!**

All stats are now perfectly aligned with your Google Sheets structure and accessible through:
- **Dashboard clickable breakdowns** with detailed insights
- **Landing page direct logging** for quick stat entry  
- **Voice recognition** for hands-free logging
- **Text input** for manual entry
- **Campus-specific filtering** and validation

**Every field maps directly to your Google Sheets columns - no more data misalignment!** 🎉 