import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase credentials. Please add to .env file.');
}

export const supabase = createClient(supabaseUrl || '', supabaseAnonKey || '');

// Get or create device ID
export function getDeviceId() {
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('device_id', deviceId);
  }
  return deviceId;
}

// Fetch waiting requests
export async function fetchWaitingRequests(category) {
  const { data, error } = await supabase
    .from('requests')
    .select('*')
    .eq('status', 'waiting')
    .eq('category', category)
    .order('created_at', { ascending: false })
    .limit(10);

  if (error) {
    console.error('Error fetching requests:', error);
    return [];
  }
  return data || [];
}

// Fetch requests created by this device
export async function fetchMyRequests() {
  const deviceId = getDeviceId();
  const { data, error } = await supabase
    .from('requests')
    .select('*')
    .eq('device_id', deviceId)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error fetching my requests:', error);
    return [];
  }
  return data || [];
}

// Create a new request
export async function createRequest(requestData) {
  const deviceId = getDeviceId();
  
  const { data, error } = await supabase
    .from('requests')
    .insert([{
      device_id: deviceId,
      name: requestData.name,
      category: requestData.category,
      description: requestData.need,
      minutes: requestData.minutes,
      distance: requestData.distance || 'לא צוין',
      status: 'waiting'
    }])
    .select()
    .single();

  if (error) {
    console.error('Error creating request:', error);
    throw error;
  }
  return data;
}

// Update request status
export async function updateRequestStatus(requestId, status, timestamp = new Date().toISOString()) {
  const updates = { status };
  
  if (status === 'accepted') {
    updates.accepted_at = timestamp;
  } else if (status === 'in_progress') {
    updates.in_progress_at = timestamp;
  } else if (status === 'completed') {
    updates.completed_at = timestamp;
  }

  const { data, error } = await supabase
    .from('requests')
    .update(updates)
    .eq('id', requestId)
    .select()
    .single();

  if (error) {
    console.error('Error updating request:', error);
    throw error;
  }
  return data;
}

// Check if device has active request for a person
export async function hasActiveRequest(name) {
  const deviceId = getDeviceId();
  
  const { data, error } = await supabase
    .from('requests')
    .select('id')
    .eq('device_id', deviceId)
    .eq('name', name)
    .neq('status', 'completed')
    .limit(1);

  if (error) {
    console.error('Error checking active request:', error);
    return false;
  }
  return data && data.length > 0;
}
