import './UserList.css';

const UserList = ({ users, onEdit, onDelete }) => {
  return (
    <div className="glass-panel list-container fade-in">
      <h2>Registered Users</h2>
      {users.length === 0 ? (
        <div className="empty-state">
          <p>No users found. Create one to get started.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="user-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, index) => (
                <tr key={user.id} className="row-enter" style={{ animationDelay: `${index * 0.1}s` }}>
                  <td>{user.id}</td>
                  <td>
                    <div className="user-name-cell">
                      <div className="avatar">{user.name.charAt(0).toUpperCase()}</div>
                      {user.name}
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`role-badge role-${user.role.toLowerCase()}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button onClick={() => onEdit(user)} className="btn-icon edit" title="Edit User">
                        ✎
                      </button>
                      <button onClick={() => onDelete(user.id)} className="btn-icon delete" title="Delete User">
                        ✖
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UserList;
