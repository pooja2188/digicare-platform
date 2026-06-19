// controllers/patientController.js
const Patient = require('../models/patient');
const User = require('../models/user');
const Doctor = require('../models/doctor');

exports.registerPatient = async (req, res) => {
  try {
    console.log('Request body:', req.body);
    console.log('Files:', req.files);

    // Destructure fields from req.body
    // Note: the patient form sends "name" as the full name and "familyHistory" for familyMedicalHistory
    const {
      name, // maps to fullName in your model
      email,
      phone,
      dob,
      gender,
      age,
      maritalStatus,
      bloodGroup,
      address,
      medicalHistory,
      currentMedications,
      familyHistory // maps to familyMedicalHistory
    } = req.body;

    // Extract Cloudinary URLs from files
    const profileImageFiles = req.files.profileImage;
    const documentsFiles = req.files.documents;
    const profilePhoto = profileImageFiles && profileImageFiles[0] ? profileImageFiles[0].path : null;
    const documents = documentsFiles ? documentsFiles.map(file => file.path) : [];

    // Validate required fields
    if (!name || !email || !phone || !dob || !gender || !age ||
        !maritalStatus || !bloodGroup || !address || !medicalHistory || !familyHistory) {
      return res.status(400).json({
        error: 'All required fields must be provided',
        missingFields: {
          name: !name,
          email: !email,
          phone: !phone,
          dob: !dob,
          gender: !gender,
          age: !age,
          maritalStatus: !maritalStatus,
          bloodGroup: !bloodGroup,
          address: !address,
          medicalHistory: !medicalHistory,
          familyHistory: !familyHistory
        }
      });
    }

    // Create a new Patient document (assuming you're using Mongoose)
    const newPatient = new Patient({
      fullName: name,
      email,
      phoneNumber: phone,
      dateOfBirth: new Date(dob),
      gender,
      age: parseInt(age, 10),
      maritalStatus,
      bloodGroup,
      address,
      medicalHistory,
      currentMedications,
      familyMedicalHistory: familyHistory,
      profilePhoto,
      documents,
    });

    await newPatient.save();

    // Optionally, update a corresponding user record if necessary
    const user = await User.findOne({ email });
    if (user) {
      user.userType = 'patient';
      user.typeId = newPatient._id;
      user.profileCompleted = true;
      await user.save();
    }

    res.status(201).json({
      message: 'Patient registered successfully',
      patient: {
        id: newPatient._id,
        fullName: newPatient.fullName,
        email: newPatient.email,
        gender: newPatient.gender,
        bloodGroup: newPatient.bloodGroup,
      }
    });
  } catch (error) {
    console.error('Patient registration error:', error);
    res.status(500).json({
      error: 'Failed to register patient',
      details: error.message
    });
  }
};

// Get patient profile
exports.getPatientProfile = async (req, res) => {
  try {
    const patientId = req.params.id;
    
    const patient = await Patient.findById(patientId);
    
    if (!patient) {
      return res.status(404).json({ message: 'Patient not found' });
    }
    
    res.status(200).json(patient);
  } catch (error) {
    console.error('Error fetching patient profile:', error);
    res.status(500).json({ 
      error: 'Failed to fetch patient profile',
      details: error.message 
    });
  }
};

// controllers/patient.js - updatePatientProfile controller function

exports.updatePatientProfile = async (req, res) => {
  try {
    const patientId = req.params.id;
    console.log('Update request body:', req.body);
    console.log('Files:', req.files);
    
    // Check if patient exists
    const patient = await Patient.findById(patientId);
    if (!patient) {
      return res.status(404).json({ message: 'Patient not found' });
    }
    
    // Extract fields from request body
    const {
      name,  // maps to fullName
      phone, // maps to phoneNumber
      dob,   // maps to dateOfBirth
      gender,
      age,
      maritalStatus,
      bloodGroup,
      address,
      medicalHistory,
      currentMedications,
      familyHistory // maps to familyMedicalHistory
    } = req.body;
    
    // Process files if they exist
    let profilePhoto = patient.profilePhoto;
    if (req.files && req.files.profileImage && req.files.profileImage[0]) {
      profilePhoto = req.files.profileImage[0].path;
    }
    
    // Process document files if they exist
    let documents = patient.documents || [];
    if (req.files && req.files.documents) {
      const newDocuments = req.files.documents.map(file => file.path);
      // Append new documents to existing ones
      documents = [...documents, ...newDocuments];
    }
    
    // Create update object with only the fields that were provided
    const updateData = {};
    if (name) updateData.fullName = name;
    if (phone) updateData.phoneNumber = phone;
    if (dob) updateData.dateOfBirth = new Date(dob);
    if (gender) updateData.gender = gender;
    if (age) updateData.age = parseInt(age, 10);
    if (maritalStatus) updateData.maritalStatus = maritalStatus;
    if (bloodGroup) updateData.bloodGroup = bloodGroup;
    if (address) updateData.address = address;
    if (medicalHistory) updateData.medicalHistory = medicalHistory;
    if (currentMedications !== undefined) updateData.currentMedications = currentMedications;
    if (familyHistory) updateData.familyMedicalHistory = familyHistory;
    if (profilePhoto) updateData.profilePhoto = profilePhoto;
    if (documents.length > 0) updateData.documents = documents;
    
    // Update the patient record
    const updatedPatient = await Patient.findByIdAndUpdate(
      patientId,
      { $set: updateData },
      { new: true } // Return the updated document
    );
    
    res.status(200).json({
      message: 'Patient profile updated successfully',
      patient: updatedPatient
    });
    
  } catch (error) {
    console.error('Error updating patient profile:', error);
    res.status(500).json({
      error: 'Failed to update patient profile',
      details: error.message
    });
  }
};

// This is already in your controller, no need to modify:
exports.removeDocument = async (req, res) => {
  try {
    const { patientId, documentUrl } = req.body;
    
    if (!patientId || !documentUrl) {
      return res.status(400).json({ 
        message: 'Patient ID and document URL are required' 
      });
    }
    
    const patient = await Patient.findById(patientId);
    
    if (!patient) {
      return res.status(404).json({ message: 'Patient not found' });
    }
    
    // Remove the document URL from the documents array
    const updatedDocuments = patient.documents.filter(doc => doc !== documentUrl);
    
    // Update the patient record
    await Patient.findByIdAndUpdate(
      patientId,
      { $set: { documents: updatedDocuments } }
    );
    
    res.status(200).json({
      message: 'Document removed successfully',
      remainingDocuments: updatedDocuments
    });
    
  } catch (error) {
    console.error('Error removing document:', error);
    res.status(500).json({
      error: 'Failed to remove document',
      details: error.message
    });
  }
};

// Delete patient profile
exports.deletePatientProfile = async (req, res) => {
  try {
    const patientId = req.params.id;
    
    // Find patient by ID
    const patient = await Patient.findById(patientId);
    
    if (!patient) {
      return res.status(404).json({ message: 'Patient not found' });
    }
    
    // Get the email to find associated user
    const patientEmail = patient.email;
    
    // Delete the patient document
    await Patient.findByIdAndDelete(patientId);
    
    // Update the associated user
    const user = await User.findOne({ email: patientEmail });
    if (user) {
      // Two options:
      // 1. Reset user to have no patient type and ID
      user.userType = null;
      user.typeId = null;
      user.profileCompleted = false;
      await user.save();
      
      // 2. Alternative: delete the user account completely
      // await User.findByIdAndDelete(user._id);
    }
    
    res.status(200).json({
      message: 'Patient profile deleted successfully'
    });
    
  } catch (error) {
    console.error('Error deleting patient profile:', error);
    res.status(500).json({
      error: 'Failed to delete patient profile',
      details: error.message
    });
  }
};

// Remove a document from patient profile
exports.removeDocument = async (req, res) => {
  try {
    const { patientId, documentUrl } = req.body;
    
    if (!patientId || !documentUrl) {
      return res.status(400).json({ 
        message: 'Patient ID and document URL are required' 
      });
    }
    
    const patient = await Patient.findById(patientId);
    
    if (!patient) {
      return res.status(404).json({ message: 'Patient not found' });
    }
    
    // Remove the document URL from the documents array
    const updatedDocuments = patient.documents.filter(doc => doc !== documentUrl);
    
    // Update the patient record
    await Patient.findByIdAndUpdate(
      patientId,
      { $set: { documents: updatedDocuments } }
    );
    
    res.status(200).json({
      message: 'Document removed successfully',
      remainingDocuments: updatedDocuments
    });
    
  } catch (error) {
    console.error('Error removing document:', error);
    res.status(500).json({
      error: 'Failed to remove document',
      details: error.message
    });
  }
};

// Get all patients with search functionality
exports.getAllPatients = async (req, res) => {
  try {
    const { search } = req.query;
    let query = {};

    // If search query exists, search by name
    if (search) {
      query.fullName = { $regex: search, $options: 'i' };
    }

    const patients = await Patient.find(query).select('fullName email gender age bloodGroup medicalHistory');

    res.status(200).json({
      count: patients.length,
      patients: patients.map(patient => ({
        id: patient._id,
        name: patient.fullName,
        email: patient.email,
        gender: patient.gender,
        age: patient.age,
        bloodGroup: patient.bloodGroup,
        condition: patient.medicalHistory
      }))
    });
  } catch (error) {
    console.error('Error fetching patients:', error);
    res.status(500).json({
      error: 'Failed to fetch patients',
      details: error.message
    });
  }
};

// Add patient to doctor's list
// exports.addPatientToDoctor = async (req, res) => {
//   try {
//     const { doctorId, patientId } = req.body;

//     if (!doctorId || !patientId) {
//       return res.status(400).json({
//         error: 'Doctor ID and Patient ID are required'
//       });
//     }

//     // Find both doctor and patient
//     const doctor = await Doctor.findById(doctorId);
//     const patient = await Patient.findById(patientId);

//     if (!doctor || !patient) {
//       return res.status(404).json({
//         error: 'Doctor or Patient not found'
//       });
//     }

//     // Check if patient is already in doctor's list
//     if (doctor.patients.includes(patientId)) {
//       return res.status(400).json({
//         error: 'Patient is already in doctor\'s list'
//       });
//     }

//     // Add patient to doctor's list
//     doctor.patients.push(patientId);
//     await doctor.save();

//     // Add doctor to patient's list
//     patient.doctors.push(doctorId);
//     await patient.save();

//     res.status(200).json({
//       message: 'Patient added to doctor\'s list successfully',
//       doctor: {
//         id: doctor._id,
//         fullName: doctor.fullName,
//         patients: doctor.patients
//       }
//     });
//   } catch (error) {
//     console.error('Error adding patient to doctor:', error);
//     res.status(500).json({
//       error: 'Failed to add patient to doctor',
//       details: error.message
//     });
//   }
// };



// Open Backend/controllers/patient.js and overwrite the addPatientToDoctor function:
  // Ensure Doctor model is imported at top

exports.addPatientToDoctor = async (req, res) => {
  try {
    const { doctorId, patientId, email, name, fullName, age, gender, medicalHistory, bloodGroup, dateOfBirth } = req.body;

    if (!doctorId) {
      return res.status(400).json({
        error: 'Doctor ID is required to link a patient'
      });
    }

    // Find the logged-in doctor profile inside your database collection rows
    const doctor = await Doctor.findById(doctorId);
    if (!doctor) {
      return res.status(404).json({
        error: 'Doctor profile record not found'
      });
    }

    let patient = null;

    // 1. If a patientId was provided, look up that existing patient
    if (patientId) {
      patient = await Patient.findById(patientId);
    } 
    // 2. If no patientId but an email was provided, check if the patient already exists by email
    else if (email) {
      patient = await Patient.findOne({ email });
    }

    // 3. ✅ DYNAMIC FALLBACK: If the patient doesn't exist yet, create a brand-new patient record automatically!
    if (!patient) {
      console.log("No existing patient found. Creating a fresh patient profile record inside MongoDB Atlas...");
      patient = new Patient({
        fullName: fullName || name || "New Patient",
        email: email || `patient_${Date.now()}@digicare.com`,
        age: age || 25,
        gender: gender || "Not Specified",
        bloodGroup: bloodGroup || "N/A",
        medicalHistory: medicalHistory || "None",
        dateOfBirth: dateOfBirth || null,
        documents: req.body.documents || []
      });
      await patient.save();
    }

    // 4. Check if this patient is already linked to this doctor's list to avoid duplicates
    if (doctor.patients.includes(patient._id)) {
      return res.status(400).json({
        error: 'This patient is already linked under your clinical care list'
      });
    }

    // 5. Link them up bidirectionally! Add patient to doctor, and doctor to patient
    doctor.patients.push(patient._id);
    await doctor.save();

    // Ensure the patients model supports a doctors array before pushing to clear property crash traps
    if (!patient.doctors) patient.doctors = [];
    patient.doctors.push(doctorId);
    await patient.save();

    console.log("Successfully linked new patient chart profile to doctor database arrays!");
    
    res.status(200).json({
      message: 'Patient added to doctor\'s list successfully',
      patient,
      doctor: {
        id: doctor._id,
        fullName: doctor.fullName,
        patients: doctor.patients
      }
    });
  } catch (error) {
    console.error('Error adding patient to doctor:', error);
    res.status(500).json({
      error: 'Failed to add patient to doctor',
      details: error.message
    });
  }
};
