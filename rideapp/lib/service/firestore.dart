import 'package:cloud_firestore/cloud_firestore.dart';

class FirestoreService {
  // get data
  final CollectionReference readings =
      FirebaseFirestore.instance.collection('readings3');
  final CollectionReference score =
      FirebaseFirestore.instance.collection('score_1');

  // create data
  Future<void> addData(double ax, double ay, double az, double gx, double gy,
      double gz, double mx, double my, double mz, double lat, double long) {
    return readings.add({
      'timestamp': Timestamp.now(),
      'ax': ax,
      'ay': ay,
      'az': az,
      'gx': gx,
      'gy': gy,
      'gz': gz,
      'mx': mx,
      'my': my,
      'mz': mz,
      'Latitude': lat,
      'Longitude': long,
    });
  }

  // read data from firestore
  // Stream<QuerySnapshot> getScore() {
  //   final scoreStream =
  //       score.orderBy('timestamp', descending: true).snapshots();

  //   return scoreStream;
  // }
  Stream<QuerySnapshot> getScore() {
    final scoreStream =
        score.orderBy('timestamp', descending: true).limit(1).snapshots();
    return scoreStream;
  }
}
