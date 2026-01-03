import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { StatusBar } from 'expo-status-bar';

const API_BASE_URL = 'https://waste-classification-app.onrender.com';

// Bin color mappings
const BIN_COLORS = {
  BLUE: '#2196F3',
  GREEN: '#4CAF50',
  GRAY: '#9E9E9E',
  SPECIAL: '#F44336',
};

export default function App() {
  const [image, setImage] = useState(null);
  const [classification, setClassification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Request camera permissions and launch camera
  const takePhoto = async () => {
    try {
      // Request camera permissions
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      
      if (status !== 'granted') {
        Alert.alert(
          'Permission Required',
          'Camera permission is required to take photos for waste classification.',
          [{ text: 'OK' }]
        );
        return;
      }

      // Launch camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: false,
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const imageUri = result.assets[0].uri;
        setImage(imageUri);
        setError(null);
        setClassification(null);
        
        // Automatically classify the image
        await classifyImage(imageUri);
      }
    } catch (err) {
      console.error('Error taking photo:', err);
      setError('Failed to take photo. Please try again.');
    }
  };

  // Upload image to classification API
  const classifyImage = async (uri) => {
    setLoading(true);
    setError(null);

    try {
      // Create FormData for image upload
      const formData = new FormData();
      formData.append('image', {
        uri: uri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });
      formData.append('jurisdiction_id', 'CA_DEFAULT');

      const response = await fetch(`${API_BASE_URL}/v1/classify`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setClassification(data);
      } else {
        setError(data.error?.message || 'Classification failed. Please try again.');
      }
    } catch (err) {
      console.error('Error classifying image:', err);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle clarification answer
  const handleClarification = async (answer) => {
    if (!classification?.clarification) return;

    setLoading(true);
    setError(null);

    try {
      const payload = {
        request_id: classification.request_id,
        question_id: classification.clarification.question_id,
        answer: answer,
        top_labels: classification.result?.top_labels || [],
      };

      const response = await fetch(`${API_BASE_URL}/v1/clarify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setClassification(data);
      } else {
        setError(data.error?.message || 'Clarification failed. Please try again.');
      }
    } catch (err) {
      console.error('Error submitting clarification:', err);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Reset to initial state
  const reset = () => {
    setImage(null);
    setClassification(null);
    setError(null);
  };

  // Render home screen
  const renderHome = () => (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>Waste Sorter</Text>
        <Text style={styles.subtitle}>Take a photo to identify waste items</Text>
      </View>
      
      <View style={styles.content}>
        <TouchableOpacity style={styles.cameraButton} onPress={takePhoto}>
          <Text style={styles.cameraButtonText}>📷 Take Photo</Text>
        </TouchableOpacity>
        <Text style={styles.hint}>
          Point your camera at a waste item to get bin recommendations
        </Text>
      </View>
    </View>
  );

  // Render loading state
  const renderLoading = () => (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>Waste Sorter</Text>
      </View>
      
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>Analyzing image...</Text>
      </View>
    </View>
  );

  // Render result view
  const renderResult = () => {
    const result = classification?.result;
    const binColor = BIN_COLORS[result?.bin] || '#666';

    return (
      <ScrollView style={styles.container}>
        <StatusBar style="dark" />
        <View style={styles.header}>
          <Text style={styles.title}>Waste Sorter</Text>
        </View>

        {/* Image Preview */}
        {image && (
          <View style={styles.imageContainer}>
            <Image source={{ uri: image }} style={styles.image} />
          </View>
        )}

        {/* Error Display */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>⚠️ {error}</Text>
          </View>
        )}

        {/* Result Display */}
        {result && (
          <View style={styles.resultContainer}>
            <View style={[styles.binBadge, { backgroundColor: binColor }]}>
              <Text style={styles.binText}>{result.bin}</Text>
              <Text style={styles.binLabel}>{result.bin_label}</Text>
            </View>

            <View style={styles.confidenceContainer}>
              <Text style={styles.confidenceLabel}>Confidence:</Text>
              <Text style={styles.confidenceValue}>
                {result.confidence} ({(result.confidence_score * 100).toFixed(0)}%)
              </Text>
            </View>

            {/* Rationale */}
            {result.rationale && result.rationale.length > 0 && (
              <View style={styles.rationaleContainer}>
                <Text style={styles.rationaleTitle}>Why this bin?</Text>
                {result.rationale.map((item, index) => (
                  <View key={index} style={styles.rationaleItem}>
                    <Text style={styles.rationaleType}>{item.type}:</Text>
                    <Text style={styles.rationaleText}>{item.text}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Special Handling */}
            {classification.special_handling && (
              <View style={styles.specialHandlingContainer}>
                <Text style={styles.specialHandlingTitle}>
                  ⚠️ Special Handling Required
                </Text>
                <Text style={styles.specialHandlingCategory}>
                  {classification.special_handling.category}
                </Text>
                <Text style={styles.specialHandlingInstructions}>
                  {classification.special_handling.instructions}
                </Text>
              </View>
            )}
          </View>
        )}

        {/* Clarification */}
        {classification?.needs_clarification && classification.clarification && (
          <View style={styles.clarificationContainer}>
            <Text style={styles.clarificationTitle}>Need more information:</Text>
            <Text style={styles.clarificationQuestion}>
              {classification.clarification.question_text}
            </Text>
            <View style={styles.clarificationButtons}>
              <TouchableOpacity
                style={styles.clarificationButton}
                onPress={() => handleClarification(true)}
                disabled={loading}
              >
                <Text style={styles.clarificationButtonText}>Yes</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.clarificationButton}
                onPress={() => handleClarification(false)}
                disabled={loading}
              >
                <Text style={styles.clarificationButtonText}>No</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* New Photo Button */}
        <TouchableOpacity style={styles.newPhotoButton} onPress={reset}>
          <Text style={styles.newPhotoButtonText}>Take Another Photo</Text>
        </TouchableOpacity>

        <View style={{ height: 40 }} />
      </ScrollView>
    );
  };

  // Main render logic
  if (loading) {
    return renderLoading();
  }

  if (image || classification || error) {
    return renderResult();
  }

  return renderHome();
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f6f7f9',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#e6e8ec',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  subtitle: {
    fontSize: 14,
    color: '#667085',
    marginTop: 4,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  cameraButton: {
    backgroundColor: '#111827',
    paddingHorizontal: 40,
    paddingVertical: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  hint: {
    fontSize: 14,
    color: '#667085',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#111827',
    fontWeight: '600',
  },
  imageContainer: {
    backgroundColor: '#fff',
    margin: 16,
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#e6e8ec',
  },
  image: {
    width: '100%',
    height: 300,
    resizeMode: 'cover',
  },
  errorContainer: {
    backgroundColor: '#fee',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#fcc',
  },
  errorText: {
    color: '#c00',
    fontSize: 14,
  },
  resultContainer: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e6e8ec',
  },
  binBadge: {
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  binText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  binLabel: {
    color: '#fff',
    fontSize: 16,
    marginTop: 4,
  },
  confidenceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#e6e8ec',
  },
  confidenceLabel: {
    fontSize: 14,
    color: '#667085',
  },
  confidenceValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  rationaleContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e6e8ec',
  },
  rationaleTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  rationaleItem: {
    marginBottom: 12,
  },
  rationaleType: {
    fontSize: 12,
    color: '#667085',
    fontWeight: '600',
    marginBottom: 2,
  },
  rationaleText: {
    fontSize: 14,
    color: '#111827',
    lineHeight: 20,
  },
  specialHandlingContainer: {
    marginTop: 16,
    padding: 16,
    backgroundColor: '#fff3cd',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ffc107',
  },
  specialHandlingTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 8,
  },
  specialHandlingCategory: {
    fontSize: 14,
    fontWeight: '600',
    color: '#856404',
    marginBottom: 8,
  },
  specialHandlingInstructions: {
    fontSize: 14,
    color: '#856404',
    lineHeight: 20,
  },
  clarificationContainer: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e6e8ec',
  },
  clarificationTitle: {
    fontSize: 14,
    color: '#667085',
    marginBottom: 8,
  },
  clarificationQuestion: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  clarificationButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  clarificationButton: {
    flex: 1,
    backgroundColor: '#fff',
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#d0d5dd',
    alignItems: 'center',
  },
  clarificationButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  newPhotoButton: {
    backgroundColor: '#111827',
    margin: 16,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  newPhotoButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
