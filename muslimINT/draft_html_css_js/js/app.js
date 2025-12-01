// Sample book data
 let books = [
            {
                id: 1,
                title: "Le Petit Prince",
                author: "Antoine de Saint-Exupéry",
                summary: "L'histoire d'un petit prince qui voyage de planète en planète et rencontre des adultes aux comportements étranges. Une fable poétique sur l'amitié, l'amour et la condition humaine.",
                available: true,
                borrowedBy: null
            },
            {
                id: 2,
                title: "1984",
                author: "George Orwell",
                summary: "Dans une société totalitaire où Big Brother surveille tout, Winston Smith travaille au Ministère de la Vérité. Un roman dystopique sur la manipulation et le contrôle social.",
                available: false,
                borrowedBy: "Marie Dupont"
            },
            {
                id: 3,
                title: "L'Étranger",
                author: "Albert Camus",
                summary: "Meursault, un homme indifférent, tue un Arabe sur une plage d'Alger. Un récit sur l'absurdité de l'existence et l'aliénation de l'individu moderne.",
                available: true,
                borrowedBy: null
            },
            {
                id: 4,
                title: "Les Misérables",
                author: "Victor Hugo",
                summary: "L'épopée de Jean Valjean, ancien forçat en quête de rédemption dans la France du XIXe siècle. Une fresque sociale sur la justice, l'amour et la miséricorde.",
                available: true,
                borrowedBy: null
            }
        ];

        let currentMode = 'reader';
        let currentBook = null;
        let editingBookId = null;

        // DOM elements
        const readerModeBtn = document.getElementById('readerMode');
        const adminModeBtn = document.getElementById('adminMode');
        const currentModeSpan = document.getElementById('currentMode');
        const addBookBtn = document.getElementById('addBookBtn');
        const booksGrid = document.getElementById('booksGrid');
        const bookModal = document.getElementById('bookModal');
        const addBookModal = document.getElementById('addBookModal');
        const searchInput = document.getElementById('searchInput');

        // Mode switching
        readerModeBtn.addEventListener('click', () => switchMode('reader'));
        adminModeBtn.addEventListener('click', () => switchMode('admin'));

        function switchMode(mode) {
            currentMode = mode;
            
            if (mode === 'reader') {
                readerModeBtn.classList.add('bg-green-500', 'text-white');
                readerModeBtn.classList.remove('text-gray-600');
                adminModeBtn.classList.remove('bg-green-500', 'text-white');
                adminModeBtn.classList.add('text-gray-600');
                currentModeSpan.textContent = 'Lecteur';
                addBookBtn.classList.add('hidden');
            } else {
                adminModeBtn.classList.add('bg-green-500', 'text-white');
                adminModeBtn.classList.remove('text-gray-600');
                readerModeBtn.classList.remove('bg-green-500', 'text-white');
                readerModeBtn.classList.add('text-gray-600');
                currentModeSpan.textContent = 'Administrateur';
                addBookBtn.classList.remove('hidden');
            }
            
            renderBooks();
        }

        // Search functionality
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filteredBooks = books.filter(book => 
                book.title.toLowerCase().includes(searchTerm) ||
                book.author.toLowerCase().includes(searchTerm)
            );
            renderBooks(filteredBooks);
        });

        // Render books
        function renderBooks(booksToRender = books) {
            booksGrid.innerHTML = '';
            
            booksToRender.forEach(book => {
                const bookCard = document.createElement('div');
                bookCard.className = 'book-card bg-white rounded-xl shadow-md overflow-hidden cursor-pointer';
                bookCard.onclick = () => openBookModal(book);
                
                bookCard.innerHTML = `
                    <div class="h-48 bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white text-6xl">
                        📖
                    </div>
                    <div class="p-4">
                        <h3 class="font-bold text-lg text-gray-900 mb-1 line-clamp-2">${book.title}</h3>
                        <p class="text-gray-600 text-sm mb-2">${book.author}</p>
                        <div class="flex items-center justify-between">
                            <span class="inline-block px-2 py-1 rounded-full text-xs font-medium ${
                                book.available 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                            }">
                                ${book.available ? '✅ Disponible' : '❌ Emprunté'}
                            </span>
                        </div>
                    </div>
                `;
                
                booksGrid.appendChild(bookCard);
            });
        }

        // Book modal functions
        function openBookModal(book) {
            currentBook = book;
            
            document.getElementById('modalTitle').textContent = book.title;
            document.getElementById('modalAuthor').textContent = book.author;
            document.getElementById('modalSummary').textContent = book.summary;
            
            const statusSpan = document.getElementById('modalStatus');
            if (book.available) {
                statusSpan.textContent = '✅ Disponible';
                statusSpan.className = 'inline-block px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800';
            } else {
                statusSpan.textContent = `❌ Emprunté par ${book.borrowedBy}`;
                statusSpan.className = 'inline-block px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800';
            }
            
            // Show/hide buttons based on mode and book status
            const borrowBtn = document.getElementById('borrowBtn');
            const returnBtn = document.getElementById('returnBtn');
            const editBtn = document.getElementById('editBtn');
            const deleteBtn = document.getElementById('deleteBtn');
            
            borrowBtn.classList.add('hidden');
            returnBtn.classList.add('hidden');
            editBtn.classList.add('hidden');
            deleteBtn.classList.add('hidden');
            
            if (currentMode === 'reader') {
                if (book.available) {
                    borrowBtn.classList.remove('hidden');
                } else {
                    returnBtn.classList.remove('hidden');
                }
            } else {
                editBtn.classList.remove('hidden');
                deleteBtn.classList.remove('hidden');
                if (book.available) {
                    borrowBtn.classList.remove('hidden');
                } else {
                    returnBtn.classList.remove('hidden');
                }
            }
            
            bookModal.classList.remove('hidden');
        }

        // Modal event listeners
        document.getElementById('closeModal').addEventListener('click', () => {
            bookModal.classList.add('hidden');
        });

        document.getElementById('borrowBtn').addEventListener('click', () => {
            if (currentBook && currentBook.available) {
                currentBook.available = false;
                currentBook.borrowedBy = currentMode === 'reader' ? 'Vous' : 'Utilisateur';
                renderBooks();
                openBookModal(currentBook);
            }
        });

        document.getElementById('returnBtn').addEventListener('click', () => {
            if (currentBook && !currentBook.available) {
                currentBook.available = true;
                currentBook.borrowedBy = null;
                renderBooks();
                openBookModal(currentBook);
            }
        });

        document.getElementById('editBtn').addEventListener('click', () => {
            editingBookId = currentBook.id;
            document.getElementById('addBookTitle').textContent = 'Modifier le livre';
            document.getElementById('bookTitle').value = currentBook.title;
            document.getElementById('bookAuthor').value = currentBook.author;
            document.getElementById('bookSummary').value = currentBook.summary;
            bookModal.classList.add('hidden');
            addBookModal.classList.remove('hidden');
        });

        document.getElementById('deleteBtn').addEventListener('click', () => {
            if (confirm('Êtes-vous sûr de vouloir supprimer ce livre ?')) {
                books = books.filter(book => book.id !== currentBook.id);
                renderBooks();
                bookModal.classList.add('hidden');
            }
        });

        // Add book modal
        addBookBtn.addEventListener('click', () => {
            editingBookId = null;
            document.getElementById('addBookTitle').textContent = 'Ajouter un livre';
            document.getElementById('bookForm').reset();
            addBookModal.classList.remove('hidden');
        });

        document.getElementById('closeAddModal').addEventListener('click', () => {
            addBookModal.classList.add('hidden');
        });

        document.getElementById('cancelAdd').addEventListener('click', () => {
            addBookModal.classList.add('hidden');
        });

        document.getElementById('bookForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const title = document.getElementById('bookTitle').value;
            const author = document.getElementById('bookAuthor').value;
            const summary = document.getElementById('bookSummary').value;
            
            if (editingBookId) {
                const book = books.find(b => b.id === editingBookId);
                if (book) {
                    book.title = title;
                    book.author = author;
                    book.summary = summary;
                }
            } else {
                const newBook = {
                    id: Math.max(...books.map(b => b.id)) + 1,
                    title,
                    author,
                    summary,
                    available: true,
                    borrowedBy: null
                };
                books.push(newBook);
            }
            
            renderBooks();
            addBookModal.classList.add('hidden');
        });

        // Close modals when clicking outside
        bookModal.addEventListener('click', (e) => {
            if (e.target === bookModal) {
                bookModal.classList.add('hidden');
            }
        });

        addBookModal.addEventListener('click', (e) => {
            if (e.target === addBookModal) {
                addBookModal.classList.add('hidden');
            }
        });

        // Initial render
        renderBooks();

