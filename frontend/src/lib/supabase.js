import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase credentials. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env file');
}

export const supabase = createClient(supabaseUrl || '', supabaseAnonKey || '');

// Generate UUID v4
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Get or create persistent device ID
export function getDeviceId() {
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    deviceId = generateUUID();
    localStorage.setItem('device_id', deviceId);
    console.log('Created new device ID:', deviceId);
  }
  return deviceId;
}

// Fetch ONE waiting request by category (oldest first)
export async function fetchWaitingRequest(category) {
  const { data, error } = await supabase
    .from('requests')
    .select('*')
    .eq('status', 'waiting')
    .eq('category', category)
    .order('created_at', { ascending: true })
    .limit(1)
    .single();

  if (error) {
    if (error.code === 'PGRST116') {
      // No rows returned - this is expected when no requests available
      return null;
    }
    console.error('Error fetching request:', error);
    return null;
  }
  return data;
}

// Fetch all requests created by this device
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
export async function createRequest(formData) {
  const deviceId = getDeviceId();
  
  const { data, error } = await supabase
    .from('requests')
    .insert([{
      device_id: deviceId,
      name: formData.name,
      category: formData.category,
      description: formData.need,
      minutes: parseInt(formData.minutes),
      distance: formData.distance || 'לא צוין',
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

// Update request status with optional condition check
export async function updateRequestStatus(requestId, status, requireCurrentStatus = null) {
  const updates = { status };
  const now = new Date().toISOString();
  
  if (status === 'accepted') {
    updates.accepted_at = now;
  } else if (status === 'in_progress') {
    updates.in_progress_at = now;
  } else if (status === 'completed') {
    updates.completed_at = now;
  }

  // Build query
  let query = supabase
    .from('requests')
    .update(updates)
    .eq('id', requestId);
  
  // Add conditional check if required (for preventing race conditions)
  if (requireCurrentStatus) {
    query = query.eq('status', requireCurrentStatus);
  }
  
  const { data, error, count } = await query.select();

  if (error) {
    console.error('Error updating request status:', error);
    throw error;
  }
  
  // Check if any rows were updated
  if (!data || data.length === 0) {
    return { success: false, data: null };
  }
  
  return { success: true, data: data[0] };
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
