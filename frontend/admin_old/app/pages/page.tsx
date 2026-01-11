import { mockPagesResponse } from "@/lib/mocks/pages"

export default function PagesListPage() {
  const { items, has_more } = mockPagesResponse

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Pages</h1>
        <button className="px-4 py-2 bg-black text-white rounded">
          + New Page
        </button>
      </div>

      <div className="border rounded overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left">
            <tr>
              <th className="p-3">Title</th>
              <th className="p-3">Status</th>
              <th className="p-3">Last Updated</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((page) => (
              <tr key={page.id} className="border-t">
                <td className="p-3 font-medium">{page.title}</td>
                <td className="p-3">
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      page.status === "published"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {page.status}
                  </span>
                </td>
                <td className="p-3">
                  {new Date(page.updated_at).toLocaleString()}
                </td>
                <td className="p-3 text-right">
                  <button className="text-blue-600 hover:underline">
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {has_more && (
        <div className="mt-4 text-center">
          <button className="px-4 py-2 border rounded">
            Load more
          </button>
        </div>
      )}
    </div>
  )
}
