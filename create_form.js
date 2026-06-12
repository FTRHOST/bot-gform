function createFullCopyForm() {
  var form = FormApp.create('Salinan Kuesioner Pondok Pesantren Nurul Asna');
  form.setTitle('Pengaruh Gaya Kepemimpinan Ibu Nyai dan Kedisiplinan Terhadap Motivasi Santri dengan Religiusitas sebagai Variabel Moderasi di Pondok Pesantren Nurul Asna Salatiga');
  form.setDescription('Bismillahirrahmannirrahiim\n\nAssalamu’alaikum Warahmatullahi Wabarakatuh\n\nResponden yang terhormat,\nPerkenalkan saya mahasiswa yang sedang melakukan penelitian untuk skripsi. Mohon kesediaan teman-teman santri untuk mengisi kuesioner ini dengan jujur. Data yang diperoleh akan dijaga kerahasiaannya dan hanya digunakan untuk kepentingan penelitian.\n\nAtas bantuan dan partisipasinya, saya ucapkan terima kasih.\nWassalamu’alaikum Warahmatullahi Wabarakatuh.');

  // --- BAGIAN 1: IDENTITAS RESPONDEN ---
  var section1 = form.addSectionHeaderItem().setTitle('Identitas Responden');
  
  form.addTextItem().setTitle('Nama Lengkap').setRequired(true);
  
  form.addTextItem().setTitle('Usia (contoh : 20)').setRequired(true);
  
  form.addMultipleChoiceItem().setTitle('Jenis Kelamin')
    .setChoices([
      form.createChoice('Pria'),
      form.createChoice('Wanita')
    ]).setRequired(true);
    
  form.addTextItem().setTitle('Fakultas - Program Studi (contoh : Dakwah - Manajemen Dakwah)').setRequired(true);
  
  form.addMultipleChoiceItem().setTitle('Semester Saat Ini')
    .setChoices([
      form.createChoice('Semester 1 - Semester 2'),
      form.createChoice('Semester 3 - Semester 4'),
      form.createChoice('Semester 5 - Semester 6'),
      form.createChoice('Semester 7 - Semester 8'),
      form.createChoice('> Semester 9'),
      form.createChoice('Cuti atau Tidak Kuliah')
    ]).setRequired(true);

  form.addTextItem().setTitle('Asal Kota (cukup Tulis Kabupaten, contoh : Salatiga)').setRequired(true);

  form.addMultipleChoiceItem().setTitle('Jarak Tempuh dari Asal Kota ke Pesantren')
    .setChoices([
      form.createChoice('< 30 Km'),
      form.createChoice('31 - 50 Km'),
      form.createChoice('51 - 75 Km'),
      form.createChoice('76 - 100 Km'),
      form.createChoice('> 100 Km')
    ]).setRequired(true);

  form.addMultipleChoiceItem().setTitle('Uang Saku Satu Bulan')
    .setChoices([
      form.createChoice('< Rp 500.000'),
      form.createChoice('Rp 500.000 - Rp 750.000'),
      form.createChoice('Rp 760.000 - Rp 1.000.000'),
      form.createChoice('> Rp 1.000.000')
    ]).setRequired(true);

  form.addMultipleChoiceItem().setTitle('Status Saat Ini')
    .setChoices([
      form.createChoice('Santri Biasa'),
      form.createChoice('Pengurus')
    ]).setRequired(true);

  form.addMultipleChoiceItem().setTitle('Lama Menyantri saat ini')
    .setChoices([
      form.createChoice('< 1 Tahun'),
      form.createChoice('1-2 Tahun'),
      form.createChoice('3-4 Tahun'),
      form.createChoice('> 4 Tahun')
    ]).setRequired(true);

  // --- BAGIAN 2: KUESIONER ---
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
    form.addMultipleChoiceItem()
      .setTitle(questions[i])
      .setChoices(likertOptions.map(function(opt) { return form.createChoice(opt); }))
      .setRequired(true);
  }

  Logger.log('Form berhasil dibuat!');
  Logger.log('Link Edit: ' + form.getEditUrl());
  Logger.log('Link Publik: ' + form.getPublishedUrl());
}
