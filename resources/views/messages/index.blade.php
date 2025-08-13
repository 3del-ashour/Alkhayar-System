<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl leading-tight" dir="rtl">
            {{ __('messages.messages') }}
        </h2>
    </x-slot>

    <div class="py-12" dir="rtl">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-xl sm:rounded-lg p-6">
                <ul>
                    @foreach ($messages as $message)
                        <li>{{ $message->content }}</li>
                    @endforeach
                </ul>
            </div>
        </div>
    </div>
</x-app-layout>
