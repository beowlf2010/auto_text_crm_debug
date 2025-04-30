// utils/createMessage.js
export default function createMessage(lead) {
  const name = lead.firstname || 'there';
  const vehicle = [lead.VehicleYear, lead.VehicleMake, lead.VehicleModel].filter(Boolean).join(' ');
  return `🎉 Hi ${name}, check out this awesome ${vehicle || 'deal'} at Jason Pilger Chevrolet! 🚘 Call us at 251-368-4053!`;
}
