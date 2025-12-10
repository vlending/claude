import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const seoulMetroGolfCourses = [
  // 경기 북부
  {
    name: "골든비치CC",
    region: "경기북부",
    city: "남양주",
    address: "경기도 남양주시 화도읍 가곡리 232",
    latitude: 37.6892,
    longitude: 127.3345,
    holes: 27,
    par: 108,
    difficulty: 3,
    weekdayPrice: 120000,
    weekendPrice: 180000,
    bookingUrl: "https://www.goldenbeachcc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.2,
    reviewCount: 523,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나"],
  },
  {
    name: "파인밸리CC",
    region: "경기북부",
    city: "포천",
    address: "경기도 포천시 소흘읍 광릉수목원로 415",
    latitude: 37.7234,
    longitude: 127.1456,
    holes: 18,
    par: 72,
    difficulty: 4,
    weekdayPrice: 150000,
    weekendPrice: 220000,
    bookingUrl: "https://www.pinevalleycc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.5,
    reviewCount: 892,
    facilities: ["캐디", "카트", "연습장", "클럽하우스"],
  },
  {
    name: "레이크사이드CC",
    region: "경기북부",
    city: "가평",
    address: "경기도 가평군 설악면 미사리길 145",
    latitude: 37.7823,
    longitude: 127.4567,
    holes: 27,
    par: 108,
    difficulty: 3,
    weekdayPrice: 140000,
    weekendPrice: 200000,
    bookingUrl: "https://www.lakesidecc.co.kr",
    bookingOpenTime: "08:00",
    bookingOpenDays: 7,
    rating: 4.1,
    reviewCount: 645,
    facilities: ["캐디", "카트", "연습장", "수영장"],
  },

  // 경기 남부
  {
    name: "썬밸리CC",
    region: "경기남부",
    city: "용인",
    address: "경기도 용인시 처인구 양지면 남곡리 356",
    latitude: 37.2156,
    longitude: 127.4123,
    holes: 36,
    par: 144,
    difficulty: 4,
    weekdayPrice: 180000,
    weekendPrice: 280000,
    bookingUrl: "https://www.sunvalleycc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.7,
    reviewCount: 1234,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나", "레스토랑"],
  },
  {
    name: "스카이힐CC",
    region: "경기남부",
    city: "이천",
    address: "경기도 이천시 백사면 도립리 산54-1",
    latitude: 37.2234,
    longitude: 127.5567,
    holes: 27,
    par: 108,
    difficulty: 5,
    weekdayPrice: 200000,
    weekendPrice: 320000,
    bookingUrl: "https://www.skyhillcc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 14,
    rating: 4.8,
    reviewCount: 987,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "헬스장"],
  },
  {
    name: "블루원CC",
    region: "경기남부",
    city: "수원",
    address: "경기도 수원시 장안구 상광교동 376",
    latitude: 37.3156,
    longitude: 127.0234,
    holes: 18,
    par: 72,
    difficulty: 3,
    weekdayPrice: 130000,
    weekendPrice: 190000,
    bookingUrl: "https://www.blueonecc.co.kr",
    bookingOpenTime: "08:00",
    bookingOpenDays: 7,
    rating: 4.0,
    reviewCount: 456,
    facilities: ["캐디", "카트", "연습장"],
  },
  {
    name: "에버그린CC",
    region: "경기남부",
    city: "안성",
    address: "경기도 안성시 고삼면 월향리 산95",
    latitude: 37.0345,
    longitude: 127.2456,
    holes: 27,
    par: 108,
    difficulty: 4,
    weekdayPrice: 160000,
    weekendPrice: 240000,
    bookingUrl: "https://www.evergreencc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.3,
    reviewCount: 712,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나"],
  },

  // 인천
  {
    name: "베어즈베스트CC",
    region: "인천",
    city: "인천",
    address: "인천광역시 서구 금곡동 산150-1",
    latitude: 37.5234,
    longitude: 126.6345,
    holes: 18,
    par: 72,
    difficulty: 5,
    weekdayPrice: 220000,
    weekendPrice: 350000,
    bookingUrl: "https://www.bearsbestcc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 14,
    rating: 4.9,
    reviewCount: 1567,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나", "레스토랑", "숙박시설"],
  },
  {
    name: "스카이72 오션코스",
    region: "인천",
    city: "인천",
    address: "인천광역시 중구 운서동 2850",
    latitude: 37.4523,
    longitude: 126.4234,
    holes: 18,
    par: 72,
    difficulty: 4,
    weekdayPrice: 190000,
    weekendPrice: 290000,
    bookingUrl: "https://www.sky72.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.6,
    reviewCount: 2134,
    facilities: ["캐디", "카트", "연습장", "클럽하우스"],
  },

  // 경기 동부
  {
    name: "남서울CC",
    region: "경기동부",
    city: "하남",
    address: "경기도 하남시 초이동 산76",
    latitude: 37.5456,
    longitude: 127.2234,
    holes: 27,
    par: 108,
    difficulty: 3,
    weekdayPrice: 170000,
    weekendPrice: 250000,
    bookingUrl: "https://www.southseoulcc.co.kr",
    bookingOpenTime: "08:00",
    bookingOpenDays: 7,
    rating: 4.4,
    reviewCount: 834,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나"],
  },
  {
    name: "레이크우드CC",
    region: "경기동부",
    city: "광주",
    address: "경기도 광주시 곤지암읍 삼리 산137-1",
    latitude: 37.3678,
    longitude: 127.3456,
    holes: 27,
    par: 108,
    difficulty: 4,
    weekdayPrice: 155000,
    weekendPrice: 230000,
    bookingUrl: "https://www.lakewoodcc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.2,
    reviewCount: 678,
    facilities: ["캐디", "카트", "연습장", "클럽하우스"],
  },

  // 경기 서부
  {
    name: "골든레이크CC",
    region: "경기서부",
    city: "김포",
    address: "경기도 김포시 월곶면 개곡리 산21-1",
    latitude: 37.6234,
    longitude: 126.5678,
    holes: 18,
    par: 72,
    difficulty: 3,
    weekdayPrice: 140000,
    weekendPrice: 200000,
    bookingUrl: "https://www.goldenlakecc.co.kr",
    bookingOpenTime: "08:00",
    bookingOpenDays: 7,
    rating: 4.1,
    reviewCount: 512,
    facilities: ["캐디", "카트", "연습장"],
  },
  {
    name: "서서울CC",
    region: "경기서부",
    city: "파주",
    address: "경기도 파주시 탄현면 성동리 산27-1",
    latitude: 37.7456,
    longitude: 126.7234,
    holes: 27,
    par: 108,
    difficulty: 4,
    weekdayPrice: 165000,
    weekendPrice: 245000,
    bookingUrl: "https://www.westseoulcc.co.kr",
    bookingOpenTime: "07:00",
    bookingOpenDays: 7,
    rating: 4.3,
    reviewCount: 923,
    facilities: ["캐디", "카트", "연습장", "클럽하우스", "사우나"],
  },
];

async function main() {
  console.log("🌱 Starting seed...");

  // Clear existing data
  await prisma.bookingPrediction.deleteMany({});
  await prisma.alert.deleteMany({});
  await prisma.favoriteGolfCourse.deleteMany({});
  await prisma.teeTimeSlot.deleteMany({});
  await prisma.golfCourse.deleteMany({});
  await prisma.user.deleteMany({});

  console.log("✨ Cleared existing data");

  // Seed golf courses
  for (const course of seoulMetroGolfCourses) {
    await prisma.golfCourse.create({
      data: {
        ...course,
        isActive: true,
      },
    });
  }

  console.log(`✅ Created ${seoulMetroGolfCourses.length} golf courses`);

  // Create sample users
  const sampleUsers = [
    {
      email: "golfer1@example.com",
      name: "김골프",
      phone: "010-1234-5678",
      address: "서울특별시 강남구",
      latitude: 37.4979,
      longitude: 127.0276,
      averageScore: 95,
      skillLevel: "INTERMEDIATE",
      preferredDays: ["SAT", "SUN"],
      preferredTimes: ["MORNING"],
      budgetMin: 100000,
      budgetMax: 200000,
      subscriptionTier: "PREMIUM",
      notificationsEnabled: true,
    },
    {
      email: "golfer2@example.com",
      name: "이타이거",
      phone: "010-2345-6789",
      address: "경기도 수원시",
      latitude: 37.2636,
      longitude: 127.0286,
      averageScore: 88,
      skillLevel: "ADVANCED",
      preferredDays: ["MON", "WED", "FRI"],
      preferredTimes: ["AFTERNOON"],
      budgetMin: 150000,
      budgetMax: 300000,
      subscriptionTier: "FREE",
      notificationsEnabled: true,
    },
  ];

  for (const user of sampleUsers) {
    await prisma.user.create({
      data: user as any,
    });
  }

  console.log(`✅ Created ${sampleUsers.length} sample users`);

  // Create sample tee time slots (next 7 days)
  const courses = await prisma.golfCourse.findMany({ take: 5 });
  const today = new Date();

  for (let dayOffset = 0; dayOffset < 7; dayOffset++) {
    const date = new Date(today);
    date.setDate(date.getDate() + dayOffset);

    for (const course of courses) {
      // Create morning slots (7:00 - 12:00)
      for (let hour = 7; hour <= 12; hour++) {
        for (let minute = 0; minute < 60; minute += 10) {
          const time = `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}`;
          const isWeekend = date.getDay() === 0 || date.getDay() === 6;
          const price = isWeekend ? course.weekendPrice : course.weekdayPrice;
          const status = Math.random() > 0.7 ? "BOOKED" : "AVAILABLE";

          await prisma.teeTimeSlot.create({
            data: {
              golfCourseId: course.id,
              date,
              time,
              price,
              status: status as any,
              lastChecked: new Date(),
              wasCancelled: false,
            },
          });
        }
      }
    }
  }

  console.log("✅ Created sample tee time slots");

  console.log("🎉 Seed completed successfully!");
}

main()
  .catch((e) => {
    console.error("❌ Error seeding database:", e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
