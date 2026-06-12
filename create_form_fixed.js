function createFullCopyForm() {
  var form = FormApp.create('Salinan Kuesioner Pondok Pesantren Nurul Asna');
  
  form.setTitle('Pengaruh Gaya Kepemimpinan Ibu Nyai dan Kedisiplinan Terhadap Motivasi Santri dengan Religiusitas sebagai Variabel Moderasi di Pondok Pesantren Nurul Asna Salatiga');
  form.setDescription('Bismillahirrahmannirrahiim\n\nAssalamu’alaikum Warahmatullahi Wabarakatuh\n\nResponden yang terhormat,\nPerkenalkan saya mahasiswa yang sedang melakukan penelitian untuk skripsi. Mohon kesediaan teman-teman santri untuk mengisi kuesioner ini dengan jujur. Data yang diperoleh akan dijaga kerahasiaannya dan hanya digunakan untuk kepentingan penelitian.\n\nAtas bantuan dan partisipasinya, saya ucapkan terima kasih.\nWassalamu’alaikum Warahmatullahi Wabarakatuh.');

  // --- BAGIAN 1: IDENTITAS RESPONDEN ---
  form.addSectionHeaderItem().setTitle('Identitas Responden');
  
  form.addTextItem().setTitle('Nama Lengkap').setRequired(true);
  form.addTextItem().setTitle('Usia (contoh : 20)').setRequired(true);
  
  // Perbaikan: createChoice dipanggil dari item, bukan dari form
  var itemJK = form.addMultipleChoiceItem();
  itemJK.setTitle('Jenis Kelamin')
    .setChoices([
      itemJK.createChoice('Pria'),
      itemJK.createChoice('Wanita')
    ]).setRequired(true);
    
  form.addTextItem().setTitle('Fakultas - Program Studi (contoh : Dakwah - Manajemen Dakwah)').setRequired(true);
  
  var itemSem = form.addMultipleChoiceItem();
  itemSem.setTitle('Semester Saat Ini')
    .setChoices([
      itemSem.createChoice('Semester 1 - Semester 2'),
      itemSem.createChoice('Semester 3 - Semester 4'),
      itemSem.createChoice('Semester 5 - Semester 6'),
      itemSem.createChoice('Semester 7 - Semester 8'),
      itemSem.createChoice('> Semester 9'),
      itemSem.createChoice('Cuti atau Tidak Kuliah')
    ]).setRequired(true);

  form.addTextItem().setTitle('Asal Kota (cukup Tulis Kabupaten, contoh : Salatiga)').setRequired(true);

  var itemJarak = form.addMultipleChoiceItem();
  itemJarak.setTitle('Jarak Tempuh dari Asal Kota ke Pesantren')
    .setChoices([
      itemJarak.createChoice('< 30 Km'),
      itemJarak.createChoice('31 - 50 Km'),
      itemJarak.createChoice('51 - 75 Km'),
      itemJarak.createChoice('76 - 100 Km'),
      itemJarak.createChoice('> 100 Km')
    ]).setRequired(true);

  var itemUang = form.addMultipleChoiceItem();
  itemUang.setTitle('Uang Saku Satu Bulan')
    .setChoices([
      itemUang.createChoice('< Rp 500.000'),
      itemUang.createChoice('Rp 500.000 - Rp 750.000'),
      itemUang.createChoice('Rp 760.000 - Rp 1.000.000'),
      itemUang.createChoice('> Rp 1.000.000')
    ]).setRequired(true);

  var itemStatus = form.addMultipleChoiceItem();
  itemStatus.setTitle('Status Saat Ini')
    .setChoices([
      itemStatus.createChoice('Santri Biasa'),
      itemStatus.createChoice('Pengurus')
    ]).setRequired(true);

  var itemLama = form.addMultipleChoiceItem();
  itemLama.setTitle('Lama Menyantri saat ini')
    .setChoices([
      itemLama.createChoice('< 1 Tahun'),
      itemLama.createChoice('1-2 Tahun'),
      itemLama.createChoice('3-4 Tahun'),
      itemLama.createChoice('> 4 Tahun')
    ]).setRequired(true);

  // --- BAGIAN 2: KUESIONER (LIKERT SCALE) ---
  form.addPageBreakItem().setTitle('Kuesioner Penelitian')
    .setHelpText('Pilihlah salah satu jawaban yang paling sesuai dengan keadaan Anda:\n1 = Sangat Tidak Setuju (STS)\n2 = Tidak Setuju (TS)\n3 = Netral (N)\n4 = Setuju (S)\n5 = Sangat Setuju (SS)');

  var likertOptions = [
    "Sangat Tidak Setuju", 
    "Tidak Setuju", 
    "Netral", 
    "Setuju", 
    "Sangat Setuju"
  ];

  var questions = [
    "Saya berusaha semaksimal mungkin untuk mencapai hasil maksimal dalam kegiatan pesantren",
    "Saya merasa bertanggung jawab sebagai santri",
    "Lingkungan dan teman di pesantren membuat saya lebih semangat dalam kegiatan",
    "Saya ingin meningkatkan kemampuan diri selama di pesantren",
    "Ibu Nyai memberikan arahan dan teladan yang baik dalam prilaku sehari-hari",
    "Ibu Nyai sering mengingatkan pentingnya tujuan belajar dan beribadah di pesantren",
    "Ibu Nyai mendorong santri untuk berpikir dan memahami pelajaran secara mendalam",
    "Ibu Nyai memberikan nasihat atau bimbingan secara pribadi ketika santri mengalami kesulitan",
    "Saya mematuhi peraturan yang berlaku di pesantren",
    "Saya berusaha mengikuti seluruh kegiatan pesantren sesuai jadwal yang ditentukan",
    "Saya menyelesaikan tugas yang diberikan oleh pengurus atau ustadz dengan baik",
    "Saya berusaha melaksanakan ibadah wajib secara konsisten",
    "Saya merasakan ketenangan batin ketika menjalankan ibadah",
    "Saya berusaha memahami ajaran agama yang diajarkan di pesantren",
    "Nilai-nilai agama mempengaruhi perilaku saya dalam kehidupan sehari-hari"
  ];

  for (var i = 0; i < questions.length; i++) {
    var itemLikert = form.addMultipleChoiceItem();
    itemLikert.setTitle(questions[i])
      .setChoices(likertOptions.map(function(opt) { return itemLikert.createChoice(opt); }))
      .setRequired(true);
  }

  Logger.log('Form berhasil dibuat!');
  Logger.log('Link Edit: ' + form.getEditUrl());
}
