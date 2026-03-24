# Framework Test Examples

## JavaScript/TypeScript (Jest, Vitest, Mocha)

```typescript
describe('Feature', () => {
  it('should reject when user lacks permission', async () => {
    const user = createUserWithoutPermission();
    await expect(performAction(user)).rejects.toThrow(AccessDenied);
  });
});
```

## Python (pytest)

```python
def test_create_project_without_permission_fails(unauthorized_user):
    """User without permission cannot create projects."""
    with pytest.raises(PermissionError):
        create_project(user=unauthorized_user, name="test")
```

## Swift (Swift Testing)

```swift
@Test("Cannot create project without permission")
func testCreateProjectWithoutPermissionFails() async throws {
    let user = try await createUserWithoutPermission()
    await #expect(performing: {
        try await user.createProject(name: "test")
    }, throws: { $0 is AccessDeniedError })
}
```

## Go

```go
func TestCreateProjectWithoutPermission(t *testing.T) {
    user := createUserWithoutPermission(t)
    err := user.CreateProject("test")
    assert.ErrorIs(t, err, ErrAccessDenied)
}
```
