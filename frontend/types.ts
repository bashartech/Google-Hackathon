/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type ServiceType = 'AC Repair' | 'Plumbing' | 'Electrician' | 'Home Cleaning' | 'Carpenter' | 'Painter';

export type PakistaniCity = 'Karachi' | 'Lahore' | 'Islamabad';

export interface ServiceProvider {
  provider_id: string;
  name: string;
  service_type: ServiceType;
  rating: number;
  city: PakistaniCity;
  areas: string[];
  experience_years: number;
  response_time_min: number;
  emergency_available: boolean;
  hourly_rate_pkr: number;
  active_bookings_count: number;
  imageUrl?: string;
}

export interface Booking {
  booking_id: string;
  customer_name: string;
  customer_phone: string;
  customer_email: string;
  service_type: ServiceType;
  provider_id: string;
  provider_name: string;
  date: string;
  time_slot: string;
  status: 'pending_provider' | 'confirmed' | 'rejected' | 'timeout' | 'completed';
  price_pkr: number;
  is_peak_applied: boolean;
  google_calendar_synced: boolean;
  created_at: string;
}

export interface AgentReasoningStep {
  agent_name: 'Coordinator' | 'Discovery' | 'Edge Case Handler' | 'Matching & Ranking' | 'Booking & Confirmation';
  status: 'running' | 'completed' | 'warning' | 'info';
  message: string;
  timestamp: string;
  details?: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'system' | 'assistant';
  text: string;
  language?: 'English' | 'Urdu' | 'Roman Urdu';
  booking?: Booking;
  agentSteps?: AgentReasoningStep[];
}
