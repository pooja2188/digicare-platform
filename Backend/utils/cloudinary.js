// const cloudinary = require('cloudinary').v2;
// const { CloudinaryStorage } = require('multer-storage-cloudinary');
// require('dotenv').config();

// // FIXED: Using correct JavaScript colons (:) and lowercase property names
// cloudinary.config({
//   cloud_name: 'dn3bezdcq',
//   api_key: '264643833296627',
//   api_secret: 'Md7CHfLRASa17zER_-uhKuvFft4'
// });

// // Configure the cloud storage bucket folder and allowed file extensions
// const storage = new CloudinaryStorage({
//   cloudinary: cloudinary,
//   params: {
//     folder: 'digicare_secure_records',
//     allowed_formats: ['jpg', 'png', 'jpeg', 'pdf'], 
//     resource_type: 'auto' 
//   }
// });

// module.exports = { cloudinary, storage };


// utils/cloudinary.js
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');

// Configure Cloudinary using environment variables or fallback values
cloudinary.config({
  cloud_name: 'dn3bezdcq',
  api_key: '264643833296627',
  api_secret: 'Md7CHfLRASa17zER_-uhKuvFft4'
});

// Create a storage instance that configures folders/formats based on file field name
const storage = new CloudinaryStorage({
  cloudinary,
  params: (req, file) => {
    if (file.fieldname === 'profileImage') {
      // For patients (if needed in other routes)
      return {
        folder: 'patients/profile_photos',
        allowed_formats: ['jpg', 'jpeg', 'png']
      };
    } else if (file.fieldname === 'documents') {
      // For patient documents
      return {
        folder: 'patients/documents',
        allowed_formats: ['pdf'],
        resource_type: 'raw'  // Important: set to raw for PDFs and other non-image files
      };
    } else if (file.fieldname === 'profilePhoto') {
      // For doctors
      return {
        folder: 'doctors/profile_photos',
        allowed_formats: ['jpg', 'jpeg', 'png']
      };
    }
    // Default fallback
    return {
      folder: 'others'
    };
  }
});

module.exports = { cloudinary, storage };