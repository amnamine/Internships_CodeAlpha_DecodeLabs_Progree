const express = require('express');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.use(session({
  secret: 'secret-social-key-12345',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 24 * 60 * 60 * 1000, // 1 day
    httpOnly: true
  }
}));

// Helper authentication middleware
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized. Please login.' });
  }
  next();
}

// --- AUTHENTICATION ENDPOINTS ---

// Register
app.post('/api/auth/register', async (req, res) => {
  const { username, password, display_name } = req.body;
  if (!username || !password || !display_name) {
    return res.status(400).json({ error: 'All fields are required' });
  }

  try {
    const trimmedUsername = username.trim().toLowerCase();
    const existingUser = await db.get('SELECT id FROM users WHERE username = ?', [trimmedUsername]);
    if (existingUser) {
      return res.status(400).json({ error: 'Username already taken' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    // Generate a default avatar if none provided (using standard cool avatars)
    const randomSeed = Math.floor(Math.random() * 1000);
    const avatarUrl = `https://api.dicebear.com/7.x/bottts/svg?seed=${randomSeed}`;

    const result = await db.run(
      'INSERT INTO users (username, password, display_name, avatar_url, bio) VALUES (?, ?, ?, ?, ?)',
      [trimmedUsername, hashedPassword, display_name.trim(), avatarUrl, 'Hello! I am new here.']
    );

    req.session.userId = result.id;
    res.status(201).json({ message: 'User registered successfully', userId: result.id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Login
app.post('/api/auth/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required' });
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE username = ?', [username.trim().toLowerCase()]);
    if (!user) {
      return res.status(400).json({ error: 'Invalid username or password' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ error: 'Invalid username or password' });
    }

    req.session.userId = user.id;
    res.json({
      message: 'Logged in successfully',
      user: {
        id: user.id,
        username: user.username,
        display_name: user.display_name,
        avatar_url: user.avatar_url,
        bio: user.bio
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Logout
app.post('/api/auth/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Could not log out' });
    }
    res.clearCookie('connect.sid');
    res.json({ message: 'Logged out successfully' });
  });
});

// Get current user info
app.get('/api/auth/me', async (req, res) => {
  if (!req.session.userId) {
    return res.json({ user: null });
  }
  try {
    const user = await db.get('SELECT id, username, display_name, avatar_url, bio FROM users WHERE id = ?', [req.session.userId]);
    res.json({ user });
  } catch (err) {
    res.status(500).json({ error: 'Database error' });
  }
});


// --- USER PROFILE & FOLLOW ENDPOINTS ---

// Get specific user profile
app.get('/api/users/:id', async (req, res) => {
  const targetId = parseInt(req.params.id);
  const currentUserId = req.session.userId;

  try {
    const user = await db.get('SELECT id, username, display_name, avatar_url, bio, created_at FROM users WHERE id = ?', [targetId]);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const followerCountRow = await db.get('SELECT COUNT(*) as count FROM follows WHERE followed_id = ?', [targetId]);
    const followingCountRow = await db.get('SELECT COUNT(*) as count FROM follows WHERE follower_id = ?', [targetId]);
    
    let isFollowing = false;
    if (currentUserId) {
      const followRow = await db.get('SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?', [currentUserId, targetId]);
      isFollowing = !!followRow;
    }

    res.json({
      user,
      followerCount: followerCountRow.count,
      followingCount: followingCountRow.count,
      isFollowing
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Update current user profile
app.put('/api/users/profile', requireAuth, async (req, res) => {
  const { display_name, bio, avatar_url } = req.body;
  if (!display_name) {
    return res.status(400).json({ error: 'Display name is required' });
  }

  try {
    await db.run(
      'UPDATE users SET display_name = ?, bio = ?, avatar_url = ? WHERE id = ?',
      [display_name.trim(), bio ? bio.trim() : '', avatar_url ? avatar_url.trim() : '', req.session.userId]
    );
    res.json({ message: 'Profile updated successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Follow/Unfollow user toggle
app.post('/api/users/:id/follow', requireAuth, async (req, res) => {
  const followedId = parseInt(req.params.id);
  const followerId = req.session.userId;

  if (followedId === followerId) {
    return res.status(400).json({ error: 'You cannot follow yourself' });
  }

  try {
    const targetUser = await db.get('SELECT id FROM users WHERE id = ?', [followedId]);
    if (!targetUser) {
      return res.status(404).json({ error: 'User to follow not found' });
    }

    const existingFollow = await db.get(
      'SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?',
      [followerId, followedId]
    );

    if (existingFollow) {
      // Unfollow
      await db.run('DELETE FROM follows WHERE follower_id = ? AND followed_id = ?', [followerId, followedId]);
      res.json({ isFollowing: false, message: 'Unfollowed user' });
    } else {
      // Follow
      await db.run('INSERT INTO follows (follower_id, followed_id) VALUES (?, ?)', [followerId, followedId]);
      res.json({ isFollowing: true, message: 'Followed user' });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// List users for "Who to follow" suggestion
app.get('/api/users', requireAuth, async (req, res) => {
  try {
    // Get users that current user is NOT following (excluding self)
    const users = await db.all(`
      SELECT id, username, display_name, avatar_url, bio FROM users 
      WHERE id != ? 
      AND id NOT IN (SELECT followed_id FROM follows WHERE follower_id = ?)
      LIMIT 5
    `, [req.session.userId, req.session.userId]);
    res.json(users);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});


// --- POST ENDPOINTS ---

// Create post
app.post('/api/posts', requireAuth, async (req, res) => {
  const { content, image_url } = req.body;
  if (!content || !content.trim()) {
    return res.status(400).json({ error: 'Post content cannot be empty' });
  }

  try {
    const result = await db.run(
      'INSERT INTO posts (user_id, content, image_url) VALUES (?, ?, ?)',
      [req.session.userId, content.trim(), image_url ? image_url.trim() : null]
    );
    res.status(201).json({ message: 'Post created successfully', postId: result.id });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Get posts (supports filter=feed, filter=explore, filter=user&userId=X)
app.get('/api/posts', async (req, res) => {
  const currentUserId = req.session.userId;
  const filter = req.query.filter || 'explore'; // feed, explore, user
  const targetUserId = req.query.userId;

  let query = `
    SELECT p.id, p.content, p.image_url, p.created_at, p.user_id,
           u.username, u.display_name, u.avatar_url,
           (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes_count,
           (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comments_count,
           CASE WHEN ? IS NULL THEN 0 ELSE (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = ?) END as user_liked
    FROM posts p
    JOIN users u ON p.user_id = u.id
  `;

  let params = [currentUserId, currentUserId];

  if (filter === 'feed' && currentUserId) {
    // Only show posts by followed users + self
    query += ` WHERE p.user_id = ? OR p.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)`;
    params.push(currentUserId, currentUserId);
  } else if (filter === 'user' && targetUserId) {
    query += ` WHERE p.user_id = ?`;
    params.push(parseInt(targetUserId));
  }

  query += ` ORDER BY p.created_at DESC`;

  try {
    const posts = await db.all(query, params);
    res.json(posts);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Delete post
app.delete('/api/posts/:id', requireAuth, async (req, res) => {
  const postId = parseInt(req.params.id);
  try {
    const post = await db.get('SELECT user_id FROM posts WHERE id = ?', [postId]);
    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }
    if (post.user_id !== req.session.userId) {
      return res.status(403).json({ error: 'Unauthorized to delete this post' });
    }
    await db.run('DELETE FROM posts WHERE id = ?', [postId]);
    res.json({ message: 'Post deleted successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});


// --- COMMENT ENDPOINTS ---

// Get comments for a post
app.get('/api/posts/:id/comments', async (req, res) => {
  const postId = parseInt(req.params.id);
  try {
    const comments = await db.all(`
      SELECT c.id, c.content, c.created_at, c.user_id,
             u.username, u.display_name, u.avatar_url
      FROM comments c
      JOIN users u ON c.user_id = u.id
      WHERE c.post_id = ?
      ORDER BY c.created_at ASC
    `, [postId]);
    res.json(comments);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

// Add comment to a post
app.post('/api/posts/:id/comments', requireAuth, async (req, res) => {
  const postId = parseInt(req.params.id);
  const { content } = req.body;

  if (!content || !content.trim()) {
    return res.status(400).json({ error: 'Comment content cannot be empty' });
  }

  try {
    const post = await db.get('SELECT id FROM posts WHERE id = ?', [postId]);
    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }

    const result = await db.run(
      'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
      [postId, req.session.userId, content.trim()]
    );

    const comment = await db.get(`
      SELECT c.id, c.content, c.created_at, c.user_id,
             u.username, u.display_name, u.avatar_url
      FROM comments c
      JOIN users u ON c.user_id = u.id
      WHERE c.id = ?
    `, [result.id]);

    res.status(201).json(comment);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});


// --- LIKE ENDPOINTS ---

// Like/Unlike post toggle
app.post('/api/posts/:id/like', requireAuth, async (req, res) => {
  const postId = parseInt(req.params.id);
  const userId = req.session.userId;

  try {
    const post = await db.get('SELECT id FROM posts WHERE id = ?', [postId]);
    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }

    const existingLike = await db.get(
      'SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?',
      [userId, postId]
    );

    if (existingLike) {
      // Unlike
      await db.run('DELETE FROM likes WHERE user_id = ? AND post_id = ?', [userId, postId]);
      const likesCountRow = await db.get('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', [postId]);
      res.json({ liked: false, likesCount: likesCountRow.count });
    } else {
      // Like
      await db.run('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', [userId, postId]);
      const likesCountRow = await db.get('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', [postId]);
      res.json({ liked: true, likesCount: likesCountRow.count });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});


// Fallback to serving the SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start Server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
