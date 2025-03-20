import 'dart:async';
import 'package:flutter/material.dart';
import 'package:rideapp/service/firestore.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:location/location.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';

class SensorPage extends StatefulWidget {
  const SensorPage({super.key});

  @override
  _SensorPageState createState() => _SensorPageState();
}

class _SensorPageState extends State<SensorPage> {
  final FirestoreService firestoreService = FirestoreService();

  // Variables to store sensor readings
  double _accelX = 0.0, _accelY = 0.0, _accelZ = 0.0;
  double _gyroX = 0.0, _gyroY = 0.0, _gyroZ = 0.0;
  double _magX = 0.0, _magY = 0.0, _magZ = 0.0;

  double _geoLat = 0.0;
  double _geoLong = 0.0;

  StreamSubscription? _accelSubscription;
  StreamSubscription? _gyroSubscription;
  StreamSubscription? _magSubscription;
  StreamSubscription<LocationData>? _locationSubscription;

  Timer? _firestoreTimer;

  Timer? _scoreUpdateTimer;
  Map<String, dynamic>? _latestScore;

  @override
  void initState() {
    super.initState();
    _startSensorListeners();
    _startFirestoreUpdates();
    _startScoreUpdates();
    _startLocationUpdates();
  }

  @override
  void dispose() {
    _accelSubscription?.cancel();
    _gyroSubscription?.cancel();
    _magSubscription?.cancel();
    _locationSubscription?.cancel();
    _firestoreTimer?.cancel();
    _scoreUpdateTimer?.cancel();
    super.dispose();
  }

  void _startSensorListeners() {
    // Accelerometer listener
    _accelSubscription = accelerometerEvents.listen((AccelerometerEvent event) {
      setState(() {
        _accelX = event.x;
        _accelY = event.y;
        _accelZ = event.z;
      });
    });

    // Gyroscope listener
    _gyroSubscription = gyroscopeEvents.listen((GyroscopeEvent event) {
      setState(() {
        _gyroX = event.x;
        _gyroY = event.y;
        _gyroZ = event.z;
      });
    });

    // Magnetometer listener
    _magSubscription = magnetometerEvents.listen((MagnetometerEvent event) {
      setState(() {
        _magX = event.x;
        _magY = event.y;
        _magZ = event.z;
      });
    });
  }

  void _startFirestoreUpdates() {
    // Schedule a task to send data to Firestore every x seconds
    _firestoreTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      firestoreService.addData(_accelX, _accelY, _accelZ, _gyroX, _gyroY,
          _gyroZ, _magX, _magY, _magZ, _geoLat, _geoLong);
    });
  }

  void _startScoreUpdates() {
    firestoreService.getScore().listen((snapshot) {
      if (snapshot.docs.isNotEmpty) {
        setState(() {
          _latestScore = snapshot.docs.first.data() as Map<String, dynamic>;
        });
      }
    });
  }

  void _startLocationUpdates() async {
    Location location = Location();

    // Check and request location permissions
    PermissionStatus permissionStatus = await location.hasPermission();
    if (permissionStatus == PermissionStatus.denied) {
      permissionStatus = await location.requestPermission();
    }

    if (permissionStatus == PermissionStatus.granted) {
      bool isServiceEnabled = await location.serviceEnabled();
      if (!isServiceEnabled) {
        isServiceEnabled = await location.requestService();
        if (!isServiceEnabled) {
          debugPrint('Location service not enabled');
          return;
        }
      }

      // Start listening to location updates
      _locationSubscription =
          location.onLocationChanged.listen((LocationData locationData) {
        setState(() {
          _geoLat = locationData.latitude ?? 0.0;
          _geoLong = locationData.longitude ?? 0.0;
        });
      });
    } else {
      debugPrint('Location permissions denied');
    }
  }

  // @override
  // Widget build(BuildContext context) {
  //   double riskScore = (_latestScore?['risk_score'] ?? 0).toDouble();

  //   return Scaffold(
  //     appBar: AppBar(
  //       title: const Text('Sensor Readings'),
  //     ),
  //     body: Padding(
  //       padding: const EdgeInsets.all(16.0),
  //       child: Column(
  //         children: [
  //           const Text('Latest Score',
  //               style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
  //           if (_latestScore != null) ...[
  //             Text(
  //                 'Timestamp: ${_latestScore!['timestamp']?.toDate() ?? 'N/A'}'),
  //             Text('Risk Score: ${_latestScore!['risk_score'] ?? 'N/A'}'),
  //             Text(
  //                 'Cumulative Speed: ${_latestScore!['cummulative_speed'] ?? 'N/A'}'),
  //             Text('Lean Angle: ${_latestScore!['lean_angle'] ?? 'N/A'}'),
  //           ] else
  //             const Text('Fetching latest score...'),
  //           const SizedBox(height: 16),
  //           // xyz
  //           SfRadialGauge(
  //             axes: <RadialAxis>[
  //               RadialAxis(
  //                 minimum: 0,
  //                 maximum: 100,
  //                 startAngle: 180,
  //                 endAngle: 0,
  //                 showLabels: false,
  //                 showTicks: false,
  //                 axisLineStyle: const AxisLineStyle(
  //                   thickness: 20,
  //                   cornerStyle: CornerStyle.bothCurve,
  //                 ),
  //                 ranges: <GaugeRange>[
  //                   GaugeRange(
  //                     startValue: 0,
  //                     endValue: 40,
  //                     color: Colors.green,
  //                     startWidth: 20,
  //                     endWidth: 20,
  //                   ),
  //                   GaugeRange(
  //                     startValue: 40,
  //                     endValue: 70,
  //                     color: Colors.blue,
  //                     startWidth: 20,
  //                     endWidth: 20,
  //                   ),
  //                   GaugeRange(
  //                     startValue: 70,
  //                     endValue: 100,
  //                     color: Colors.red,
  //                     startWidth: 20,
  //                     endWidth: 20,
  //                   ),
  //                 ],
  //                 pointers: <GaugePointer>[
  //                   NeedlePointer(
  //                     value: riskScore,
  //                     needleColor: Colors.black,
  //                     needleLength: 0.9,
  //                     knobStyle: const KnobStyle(
  //                       color: Colors.black,
  //                       sizeUnit: GaugeSizeUnit.factor,
  //                       knobRadius: 0.05,
  //                     ),
  //                   ),
  //                 ],
  //                 annotations: <GaugeAnnotation>[
  //                   GaugeAnnotation(
  //                     widget: Text(
  //                       '${riskScore.toStringAsFixed(1)}%',
  //                       style: const TextStyle(
  //                           fontSize: 18, fontWeight: FontWeight.bold),
  //                     ),
  //                     positionFactor: 0.8,
  //                     angle: 90,
  //                   ),
  //                 ],
  //               ),
  //             ],
  //           ),
  //           // xyx
  //           const Text('Accelerometer',
  //               style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
  //           Text('X: $_accelX'),
  //           Text('Y: $_accelY'),
  //           Text('Z: $_accelZ'),
  //           const SizedBox(height: 16),
  //           const Text('Gyroscope',
  //               style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
  //           Text('X: $_gyroX'),
  //           Text('Y: $_gyroY'),
  //           Text('Z: $_gyroZ'),
  //           const SizedBox(height: 16),
  //           const Text('Magnetometer',
  //               style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
  //           Text('X: $_magX'),
  //           Text('Y: $_magY'),
  //           Text('Z: $_magZ'),
  //           const SizedBox(height: 16),
  //           const SizedBox(height: 16),
  //           const Text('Device Location',
  //               style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
  //           Text('Latitude: ${_geoLat.toStringAsFixed(6)}'),
  //           Text('Longitude: ${_geoLong.toStringAsFixed(6)}'),
  //         ],
  //       ),
  //     ),
  //   );
  // }
  @override
  Widget build(BuildContext context) {
    double riskScore = (_latestScore?['risk_score'] ?? 0).toDouble();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sensor Readings'),
      ),
      body: SingleChildScrollView(
          child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text('Latest Score',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              if (_latestScore != null) ...[
                // Text(
                //     'Timestamp: ${_latestScore!['timestamp']?.toDate() ?? 'N/A'}'),
                Text('Risk Score: ${_latestScore!['risk_score'] ?? 'N/A'}'),
                Text(
                    'Cumulative Speed: ${_latestScore!['cummulative_speed'] ?? 'N/A'}'),
                Text('Lean Angle: ${_latestScore!['lean_angle'] ?? 'N/A'}'),
              ] else
                const Text('Fetching latest score...'),
              const SizedBox(height: 16),
              SfRadialGauge(
                axes: <RadialAxis>[
                  RadialAxis(
                    minimum: 0,
                    maximum: 100,
                    startAngle: 180,
                    endAngle: 0,
                    showLabels: false,
                    showTicks: false,
                    axisLineStyle: const AxisLineStyle(
                      thickness: 20,
                      cornerStyle: CornerStyle.bothCurve,
                    ),
                    ranges: <GaugeRange>[
                      GaugeRange(
                        startValue: 0,
                        endValue: 40,
                        color: Colors.green,
                        startWidth: 20,
                        endWidth: 20,
                      ),
                      GaugeRange(
                        startValue: 40,
                        endValue: 70,
                        color: Colors.blue,
                        startWidth: 20,
                        endWidth: 20,
                      ),
                      GaugeRange(
                        startValue: 70,
                        endValue: 100,
                        color: Colors.red,
                        startWidth: 20,
                        endWidth: 20,
                      ),
                    ],
                    pointers: <GaugePointer>[
                      NeedlePointer(
                        value: riskScore,
                        needleColor: Colors.black,
                        needleLength: 0.9,
                        knobStyle: const KnobStyle(
                          color: Colors.black,
                          sizeUnit: GaugeSizeUnit.factor,
                          knobRadius: 0.05,
                        ),
                      ),
                    ],
                    annotations: <GaugeAnnotation>[
                      GaugeAnnotation(
                        widget: Text(
                          '${riskScore.toStringAsFixed(1)}%',
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        positionFactor: 0.8,
                        angle: 90,
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text('Accelerometer',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text('X: $_accelX'),
              Text('Y: $_accelY'),
              Text('Z: $_accelZ'),
              const SizedBox(height: 16),
              const Text('Gyroscope',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text('X: $_gyroX'),
              Text('Y: $_gyroY'),
              Text('Z: $_gyroZ'),
              const SizedBox(height: 16),
              const Text('Magnetometer',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text('X: $_magX'),
              Text('Y: $_magY'),
              Text('Z: $_magZ'),
              const SizedBox(height: 16),
              const Text('Device Location',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text('Latitude: ${_geoLat.toStringAsFixed(6)}'),
              Text('Longitude: ${_geoLong.toStringAsFixed(6)}'),
            ],
          ),
        ),
      )),
    );
  }
}
