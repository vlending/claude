export type SkillLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "PROFESSIONAL";
export type SubscriptionTier = "FREE" | "PREMIUM";
export type AlertType = "OPENING_SOON" | "CANCELLATION" | "RECOMMENDATION";
export type SlotStatus = "AVAILABLE" | "BOOKED" | "CANCELLED" | "MONITORING";

export interface GolfCourse {
  id: string;
  name: string;
  region: string;
  city: string;
  address: string;
  latitude: number;
  longitude: number;
  holes: number;
  par: number;
  difficulty: number;
  weekdayPrice: number;
  weekendPrice: number;
  bookingUrl: string;
  bookingOpenTime: string;
  bookingOpenDays: number;
  rating?: number;
  reviewCount: number;
  facilities: string[];
  imageUrl?: string;
  isActive: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  averageScore?: number;
  skillLevel?: SkillLevel;
  preferredDays: string[];
  preferredTimes: string[];
  budgetMin?: number;
  budgetMax?: number;
  subscriptionTier: SubscriptionTier;
  subscriptionEnd?: Date;
  notificationsEnabled: boolean;
  pushToken?: string;
}

export interface TeeTimeSlot {
  id: string;
  golfCourseId: string;
  date: Date;
  time: string;
  price: number;
  status: SlotStatus;
  lastChecked: Date;
  wasCancelled: boolean;
  cancelledAt?: Date;
}

export interface Alert {
  id: string;
  userId: string;
  type: AlertType;
  golfCourseId?: string;
  title: string;
  message: string;
  actionUrl?: string;
  isRead: boolean;
  sentAt: Date;
}
